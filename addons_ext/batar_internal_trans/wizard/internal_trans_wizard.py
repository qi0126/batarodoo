# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.exceptions import UserError

class Wizard_lines(models.TransientModel):
    _name = 'sample.trans.line'

    product_id = fields.Many2one('product.product', string='Product')
    src_location = fields.Many2one('stock.location', string='Source Location')
    dest_location = fields.Many2one('stock.location', string='Dest Location')
    qty = fields.Integer(string='Qty')

class Wizard_attributeline(models.TransientModel):
    _name = 'sample.trans.attribute'

    attribute_id = fields.Many2one('product.attribute', string='Attribute')
    value_ids = fields.Many2many('product.attribute.value', string='Attribute value')

class SampleTransWizard(models.TransientModel):
    _name = 'sample.trans.wizard'

    product_id = fields.Many2one('product.template', string='Product Template')
    process_type = fields.Selection([('auto', 'Auto'), ('template', 'Template'), ('product', 'Product')], string='Process Type', default='product')
    product_code = fields.Char(string='Product Code')
    sample_code = fields.Char(string='Sample Code')
    attribute_line_ids = fields.Many2many('sample.trans.attribute', string='Attrs')
    line_ids = fields.Many2many('sample.trans.line', string='Lines')

    @api.multi
    def confirm_auto(self):
        #存储库产品款式 - 样品库款式，推荐款式
        self.ensure_one()
        order = self.env['batar.sample.trans'].browse(self._context.get('active_ids'))[0]
        sample_location = order.location_id
        quant_obj = self.env['stock.quant']
        in_sample = quant_obj.search([('location_id', '=', sample_location.id)])
        products = []
        line_ids = []
        if self.line_ids:
            for line in self.line_ids:
                line_ids.append((4, line.id, 0))
                products.append(line.product_id.default_code.split('/')[0])
        if in_sample:
            for i in in_sample:
                code = i.product_id.default_code
                template_code = code.split('/')[0]
                if template_code not in products:
                    products.append(template_code)
        quants = quant_obj.search([('location_id', '!=', sample_location.id), ('location_id.usage', '=', 'internal'), ('qty', '>', 0), ('reservation_id', '=', None), ('location_id.name', 'ilike', '-%')])
        #筛选属于这个柜台的产品quants
        new_quants = quants.filtered(lambda r: r.product_id.product_sample_location == sample_location)
        # for quant in quants:
        for quant in new_quants:
            t_code =  quant.product_id.default_code.split('/')[0]
            if t_code in products:
                continue
            else:
                vals = {
                    'product_id': quant.product_id.id,
                    'qty': 1,
                    'src_location': quant.location_id.id,
                    'dest_location': sample_location.id,
                }
                line_ids.append((0,0,vals))
                products.append(t_code)
        if len(line_ids) == 0:
            raise UserError(u'无其他产品款式可调整')
        self.line_ids = line_ids
        return self.reopen_form()

    @api.multi
    def reopen_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'context': self._context,
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('batar_internal_trans.internal_trans_wizard_form_view').id,
            'target': 'new',
        }


    @api.onchange('product_id')
    def attribute_line_onchange(self):
        '''根据产品模板，列出对应的属性属性值'''
        attribute_line = []
        if self.product_id:
            for i in self.product_id.attribute_line_ids:
                attribute_values = {
                    'attribute_id': i.attribute_id,
                    'value_ids': i.value_ids,
                }
                attribute_line.append((0, 0, attribute_values))
            self.attribute_line_ids = attribute_line
    @api.multi
    def confirm_attributes(self):
        '''根据产品模板选择的属性，增加对应的产品规格明细行'''
        self.ensure_one()
        order = self.env['batar.sample.trans'].browse(self._context.get('active_ids'))[0]
        sample_location = order.location_id
        quant_obj = self.env['stock.quant']
        if not self.product_id:
            raise UserError(u'没有选择产品款式！')
        else:
            values = self.env['product.attribute.value']
            for value in self.attribute_line_ids:
                values += value.value_ids
            # products = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)])
            products = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id), ('product_sample_location', '=', sample_location.id)])
            line_ids = []
            inuse_location = []
            for line in self.line_ids:
                line_ids.append((4, line.id, 0))
                inuse_location.append(line.src_location.id)
            for p in products:
                attribute = p.attribute_value_ids
                same_attribute = attribute & values
                if attribute == same_attribute:
                    src_locations = quant_obj.search([('product_id', '=', p.id), ('location_id', '!=', sample_location.id), ('location_id.usage', '=', 'internal'), ('location_id.name', 'ilike', '-%')])
                    if src_locations:
                        for i in src_locations:
                            if i.location_id.id in inuse_location:
                                continue
                            vals = {
                                'product_id': p.id,
                                'qty': 1,
                                'src_location': i.location_id.id,
                                'dest_location': sample_location.id,
                            }
                            line_ids.append((0, 0, vals))
            self.line_ids = line_ids
        return self.reopen_form()
    @api.onchange('product_code')
    def onchange_sample_line(self):
        '''扫产品码，查找库存，推荐到样品调拨'''
        product_obj = self.env['product.product']
        quant_obj = self.env['stock.quant']
        order = self.env['batar.sample.trans'].browse(self._context.get('active_ids'))[0]
        line_ids = []
        inuse_location = []
        sample_location = order.location_id
        for line in self.line_ids:
            line_ids.append((4, line.id, 0))
            inuse_location.append(line.src_location.id)
        if self.product_code:
            # products = product_obj.search([('default_code', 'ilike', self.product_code)])
            #如果是样品调入
            if order.type == 'in':
                product = product_obj.search([('default_code', '=', self.product_code)])
                if product:
                    # for product in products:
                    src_locations = quant_obj.search([('product_id', '=', product.id), ('location_id', '!=', sample_location.id), ('qty', '>', 0), ('reservation_id', '=', None), ('location_id.usage', '=', 'internal'), ('location_id.name', 'ilike', '-%')])
                    if src_locations:
                        total_qty = sum(src_locations.mapped('qty'))
                        inuse_total = sum(self.line_ids.filtered(lambda x: x.product_id == product).mapped('qty'))
                        if total_qty >= inuse_total + 1:
                            for i in src_locations:
                                if i.location_id.id in inuse_location:
                                    inuse_line = self.line_ids.filtered(lambda r: r.src_location == i.location_id and r.product_id == product)
                                    qty = inuse_line.qty + 1
                                    if qty <= i.qty:
                                        inuse_line.update({'qty': qty})
                                    else:
                                        continue
                                else:
                                    vals = {
                                        'product_id': product.id,
                                        'qty': 1,
                                        'src_location': i.location_id.id,
                                        'dest_location': sample_location.id,
                                    }
                                    line_ids.append((0,0,vals))
                        else:
                            raise UserError(u'此产品库存不足')
                    else:
                        raise UserError(u'此产品无库存')
                    # self.line_ids = line_ids
                else:
                    raise UserError(u'不存在包含此编号的产品')
            # else:
            #     #样品调出，扫码后，先尝试转码为数字，优先货号查找，再查找内部编号
            #     try:
            #         code = int(self.product_code)
            #         search_list = [('active', '=', True), ('location_id', '=', sample_location.id), ('name', '=', code)]
            #         product = self.env['sample.location.code'].search([search_list]).product_id
            #     except:
            #         product = self.env['product.product'].search([('default_code', '=', self.product_code)])
            #     if product:
            #         vals = {
            #             'product_id': product.id,
            #             'qty': 1,
            #             'src_location': sample_location.id,
            #         }
            #         line_ids.append((0, 0, vals))
            self.line_ids = line_ids

    @api.multi
    def confirm(self):
        self.ensure_one()
        order = self.env['batar.sample.trans'].browse(self._context.get('active_ids'))[0]
        trans_lines = []
        for line in self.line_ids:
            vals = {
                'product_id': line.product_id.id,
                'src_location': line.src_location.id,
                'dest_location': order.location_id.id,
                'qty': line.qty,
            }
            trans_lines.append((0,0,vals))
        order.write({'line_ids': trans_lines})
        return True