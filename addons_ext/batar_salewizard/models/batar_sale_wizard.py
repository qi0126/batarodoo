# -*- coding:utf-8 -*-
from openerp import api, fields, models, exceptions
import logging
_logger = logging.getLogger(__name__)



class Wizard_attributeline(models.TransientModel):
    _name = 'batar.sale.wizard.line'

    attribute_id = fields.Many2one('product.attribute', string='Attribute')
    value_ids = fields.Many2many('product.attribute.value', string='Attribute value')

class Wizard_sale_line(models.TransientModel):
    _name = 'batar.wizard.sale.line'

    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Name')
    qty = fields.Integer(string='Qty')


class Sale_orderWiard(models.TransientModel):
    _name = 'batar.sale.wizard'

    product_id = fields.Many2one('product.template', string='Product template')
    # sale_line = fields.Many2many('sale.order.line', string='Added Product')
    sale_line = fields.Many2many('batar.wizard.sale.line', string='Added Product')
    test = fields.Integer(string="Test", default=1)
    attribute_value_ids = fields.Many2many('product.attribute.value', string='Attribute value')
    attribute_line_ids = fields.Many2many('batar.sale.wizard.line', string='Product Attribute')
    # attribute_line_ids = fields.Many2many('product.attribute.line', string='Product Attribute')

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

            # self.attribute_line_ids = self.product_id.attribute_line_ids
        # attribute_line = []
        # if self.product_id:
        #     for i in self.product_id.attribute_line_ids:
        #         attribute_values = {
        #             'attribute_id': i.attribute_id,
        #             'value_ids': i.value_ids,
        #         }
        #         attribute_line.append((0, 0, attribute_values))
        #     self.attribute_line_ids = attribute_line

    @api.multi
    def confirm_attributes(self):
        '''替换下面的确认按钮。'''
        self.ensure_one()
        if not self.product_id:
            raise exceptions.ValidationError(u'没有选择产品款式！')
        else:
            values = self.env['product.attribute.value']
            for value in self.attribute_line_ids:
                values += value.value_ids

            products = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)])
            line_ids = []
            for p in products:
                attribute = p.attribute_value_ids
                same_attribute = attribute & values
                name = p.name_get()[0][1]
                if p.description_sale:
                    name += '\n' + p.description_sale
                if attribute == same_attribute:
                    vals = {
                        'product_id': p.id,
                        'qty': 1,
                        'name': name,
                    }
                    line_ids.append((0,0,vals))
            self.sale_line = line_ids


            #         order_line = self.env['sale.order.line']
            #         sale_obj = self.env['sale.order']
            #         order = sale_obj.browse(self._context.get('active_ids'))[0]
            #         name = p.name_get()[0][1]
            #         if p.description_sale:
            #             name += '\n' + p.description_sale
            #         line_id = order_line.create({'product_id': p.id,
            #                                      'order_id': order.id,
            #                                      'name': name,
            #                                      'price_unit': 0.0,
            #                                      # 'product_uom_qty': p.standard_weight,
            #                                      'product_uom_qty': 20,
            #                                      'product_uom': p.uom_id.id,
            #
            #                                      })
            #         line_ids.append(line_id.id)
            # self.sale_line = self.env['sale.order.line'].search([('id', 'in', line_ids)])
        return self.reopen_form()


    @api.onchange('product_id')
    def attribute_value_onchange(self):
        if self.product_id:
            attribute = self.product_id.attribute_line_ids
            value = []
            for a in attribute:
                value.extend(a.value_ids.ids)
            self.attribute_value_ids = self.env['product.attribute.value'].search([('id', 'in', value)])


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
            'target': 'new',
        }
    @api.multi
    def confirm(self):
        self.ensure_one()
        sale_obj = self.env['sale.order']
        order = sale_obj.browse(self._context.get('active_ids'))[0]
        sale_lines = self.env['sale.order.line']
        for i in self.sale_line:
            sale_lines.create({
                'product_id': i.product_id.id,
                'order_id': order.id,
                'name': i.name,
                'product_uom_qty': i.qty,
                'product_uom': i.product_id.uom_id.id,
                'price_unit': 0.0,

            })
        return order.write({'order_line': sale_lines})
    @api.multi
    def cancel(self):
        self.ensure_one()
        if self.sale_line:
            self.sale_line.unlink()
        return True
    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    @api.multi
    def confirm_attribute(self):
        self.ensure_one()
        if not self.product_id:
            raise exceptions.ValidationError(u'没有选择产品款式！')
#        elif self.sale_line:
#            if self.sale_line[0].product_id.product_tmpl_id == self.product_id:
#                raise exceptions.ValidationError('已添加该类产品！')
        else:
            values = self.attribute_value_ids.ids
            products = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)])
            line_ids = []
            for p in products:
                attribute = p.attribute_value_ids.ids
                same_attribute = [a for a in attribute if a in values]
                tmp = list(set(attribute) - set(same_attribute))
                if len(tmp) == 0:
                    order_line = self.env['sale.order.line']
                    sale_obj = self.env['sale.order']
                    order = sale_obj.browse(self._context.get('active_ids'))[0]
                    name = p.name_get()[0][1]
                    if p.description_sale:
                        name += '\n' + p.description_sale
                    line_id = order_line.create({'product_id': p.id,
                                                 'order_id': order.id,
                                                 'name': name,
                                                 'price_unit': 0.0,
                                                 # 'product_uom_qty': p.standard_weight,
                                                 'product_uom_qty': 20,
                                                 'product_uom': p.uom_id.id,

                                                 })
                    line_ids.append(line_id.id)
            self.sale_line = self.env['sale.order.line'].search([('id', 'in', line_ids)])
        return self.reopen_form()




