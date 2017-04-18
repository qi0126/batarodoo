# -*- coding:utf-8 -*-
from openerp import api, fields, models, exceptions
import logging
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

class Purchase(models.Model):
    _inherit = 'purchase.order'

    date_planned = fields.Datetime(required=False, )
class Purchase_line(models.Model):
    _inherit = 'purchase.order.line'

    date_planned = fields.Datetime(required=False)

class Wizard_attributeline(models.TransientModel):
    _name = 'batar.purchase.wizard.line'

    attribute_id = fields.Many2one('product.attribute', string='Attribute')
    value_ids = fields.Many2many('product.attribute.value', string='Attribute value')

class Wizard_purchase_line(models.TransientModel):
    _name = 'batar.wizard.purchase.line'

    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Name')
    qty = fields.Integer(string='Qty')


class purchase_orderWiard(models.TransientModel):
    _name = 'batar.purchase.wizard'

    product_id = fields.Many2one('product.template', string='Product template')
    purchase_line = fields.Many2many('batar.wizard.purchase.line', string='Added Product')
    attribute_value_ids = fields.Many2many('product.attribute.value', string='Attribute value')
    attribute_line_ids = fields.Many2many('batar.purchase.wizard.line', string='Product Attribute')

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
            self.purchase_line = line_ids
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
        purchase_obj = self.env['purchase.order']
        order = purchase_obj.browse(self._context.get('active_ids'))[0]
        purchase_lines = self.env['purchase.order.line']
        for i in self.purchase_line:
            purchase_lines.create({
                'product_id': i.product_id.id,
                'order_id': order.id,
                'name': i.name,
                'product_qty': i.qty,
                'product_uom': i.product_id.uom_id.id,
                'price_unit': 0.0,
                'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),

            })
        return order.write({'order_line': purchase_lines})
    @api.multi
    def cancel(self):
        self.ensure_one()
        if self.purchase_line:
            self.purchase_line.unlink()
        return True
    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))




