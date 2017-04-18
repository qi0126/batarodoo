# -*- coding: utf-8 -*-
from openerp import models, api, fields
from openerp.exceptions import UserError

class BatarAdjustment(models.Model):
    _inherit = 'batar.location.adjustment'

    is_sample = fields.Boolean(string="Sample Move", default=False)

    @api.onchange('location_id')
    def onchange_is_sample(self):
        if self.location_id:
            if self.location_id.is_sample:
                self.is_sample = True
            else:
                self.is_sample = False

class Wizard_lines(models.TransientModel):
    _name = 'samplemove.line'

    product_id = fields.Many2one('product.product', string='Product')
    src_location = fields.Many2one('stock.location', string='Source Location')
    dest_location = fields.Many2one('stock.location', string='Dest Location')
    qty = fields.Integer(string='Qty')

class Wizard_attributeline(models.TransientModel):
    _name = 'samplemove.attribute.line'

    attribute_id = fields.Many2one('product.attribute', string='Attribute')
    value_ids = fields.Many2many('product.attribute.value', string='Attribute value')
class Samplemove_wizard(models.TransientModel):
    _name = 'batar.samplemove.wizard'

    product_id = fields.Many2one('product.template', string='Product template')
    attribute_line_ids = fields.Many2many('samplemove.attribute.line', string='Product Attribute')
    product_code = fields.Char(string='Product Num')
    sample_code = fields.Char(string='Sample Num')
    line_ids = fields.Many2many('samplemove.line', string='Move line')
    process_type =fields.Selection([('template', 'Product Template'), ('auto', 'Auto')], string="Process Method")

    @api.multi
    def confirm_auto(self):
        self.ensure_one()
        order = self.env['batar.location.adjustment'].browse(self._context.get('active_ids'))[0]
        sample_location = order.location_id
        quant_obj = self.env['stock.quant']
        in_sample = quant_obj.search([('location_id', '=', sample_location.id)])
        products = []
        line_ids = []
        for line in self.line_ids:
            line_ids.append((4, line.id, 0))
            products.append(line.product_id.default_code.split('/')[0])
        for i in in_sample:
            code = i.product_id.default_code
            template_code = code.split('/')[0]
            if template_code not in products:
                products.append(template_code)
        quants = quant_obj.search([('location_id', '!=', sample_location.id), ('location_id.usage', '=', 'internal'), ('location_id.name', 'ilike', '-%')])
        for quant in quants:
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
        order = self.env['batar.location.adjustment'].browse(self._context.get('active_ids'))[0]
        sample_location = order.location_id
        quant_obj = self.env['stock.quant']
        if not self.product_id:
            raise UserError(u'没有选择产品款式！')
        else:
            values = self.env['product.attribute.value']
            for value in self.attribute_line_ids:
                values += value.value_ids
            products = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)])
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
            'view_id': self.env.ref('batar_samplemove.batar_samplemovein_wizard_form').id,
            'target': 'new',
        }


    @api.onchange('sample_code')
    def onchange_sample_line(self):
        '''存储库入样品库明细'''
        product_obj = self.env['product.product']
        quant_obj = self.env['stock.quant']
        order = self.env['batar.location.adjustment'].browse(self._context.get('active_ids'))[0]
        line_ids = []
        inuse_location = []
        sample_location = order.location_id
        for line in self.line_ids:
            line_ids.append((4, line.id, 0))
            inuse_location.append(line.src_location.id)
        if self.sample_code:
            products = product_obj.search([('default_code', 'ilike', self.sample_code)])
            if products:
                for product in products:
                    src_locations = quant_obj.search([('product_id', '=', product.id), ('location_id', '!=', sample_location.id), ('location_id.usage', '=', 'internal'), ('location_id.name', 'ilike', '-%')])
                    if src_locations:
                        for i in src_locations:
                            if i.location_id.id in inuse_location:
                                continue
                            vals = {
                                'product_id': product.id,
                                'qty': 1,
                                'src_location': i.location_id.id,
                                'dest_location': sample_location.id,
                            }
                            line_ids.append((0,0,vals))
                self.line_ids = line_ids
            else:
                raise UserError(u'不存在包含此编号的产品')

    @api.onchange('product_code')
    def onchange_line(self):
        '''样品库入存储库明细'''
        product_obj = self.env['product.product']
        quant_obj = self.env['stock.quant']
        location = self.env['stock.location']
        order = self.env['batar.location.adjustment'].browse(self._context.get('active_ids'))[0]
        inuse_location = []
        line_ids = []
        for line in self.line_ids:
            inuse_location.append(line.dest_location.id)
            line_ids.append((4, line.id, 0))
        sample_location = order.location_id
        parent_location = sample_location.location_id
        res = []
        view_locs = self.env['stock.location'].search(
            [('location_id', '=', parent_location.id), ('usage', '=', 'view')])
        if self.product_code:
            product = product_obj.search([('default_code', '=', self.product_code)])
            if not product:
                raise UserError(u'样品库中无此编码的产品规格！')
            in_sample = quant_obj.search([('product_id', '=', product.id), ('location_id', '=', sample_location.id)])
            qty_sample = sum([x.qty for x in in_sample]) - sum([y.qty for y in self.line_ids if y.product_id == product])
            if qty_sample <= 0:
                raise UserError(u'样品库无此产品，请确认后再输入！')
            else:
                vals = {
                    'product_id': product.id,
                    'qty': 1,
                    'src_location': sample_location.id,
                }
                for loc in view_locs:
                    flag = False
                    if loc.child_ids:
                        for i in loc.child_ids:
                            if i.id in inuse_location:
                                continue
                            total = 0.0
                            for j in quant_obj.search([('location_id', '=', i.id)]):
                                total += j.product_id.product_volume * j.qty
                            if i.location_volume - total >= product.product_volume:
                                res.append(i.id)
                                vals['dest_location'] = i.id
                                flag = True
                                break
                        if flag:
                            break

                    else:
                        raise UserError('不存托盘库位！')
                if len(res) == 0:
                    raise UserError('所有储柜已满！')
                line_ids.append((0, 0, vals))
                self.line_ids = line_ids
                # return self.write({'line_ids': [(0,0,vals)]})

    @api.multi
    def confirm(self):
        self.ensure_one()
        order = self.env['batar.location.adjustment'].browse(self._context.get('active_ids'))[0]
        move_lines = []
        for line in self.line_ids:
            vals = {
                'product_id': line.product_id.id,
                'location_id': line.src_location.id,
                'location_dest_id': line.dest_location.id,
                'product_uom': line.product_id.uom_id.id,
                'product_uom_qty': line.qty,
                'name': 'MO:adj',
                'origin': 'SM:' + order.name
            }
            move_lines.append((0,0,vals))
        order.write({'move_ids': move_lines, 'state': 'process', 'is_sample': False})
        return True