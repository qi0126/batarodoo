# -*- coding: utf-8 -*-
from openerp import api, fields, models, exceptions
import logging
_logger = logging.getLogger(__name__)

class Mass_expense(models.TransientModel):
    _name = 'batar.product.expense'

    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    product_attribute_value = fields.Many2many('product.attribute.value', string='Product attribute')
    is_item_fee = fields.Boolean(string="Item fee?", default=False)
    is_weight_fee = fields.Boolean(string='Weight fee?', default=False)
    is_additional_fee = fields.Boolean(string='Additional fee?', default=False)
    item_fee = fields.Float(string='Item fee')
    weight_fee = fields.Float(string='Weight fee')
    additional_fee = fields.Float(string='Additional fee')
    type = fields.Selection([('all', 'All'), ('attribute', 'Attribute')], default='all')
    product_sample_location = fields.Many2one('stock.location', string='Sample Location')

    @api.onchange('product_tmpl_id')
    def onchange_product_value(self):
        if self.product_tmpl_id:
            attribute = self.product_tmpl_id.attribute_line_ids
            value = []
            for a in attribute:
                value.extend(a.value_ids.ids)
            self.product_attribute_value = self.env['product.attribute.value'].search([('id', 'in', value)])


    @api.multi
    def confirm(self):
        self.ensure_one()
        res = self.env['product.product']
        if not self.is_item_fee and not self.is_weight_fee and not self.additional_fee and not self.product_sample_location:
            raise exceptions.ValidationError(u'操作失败!')
        if self.product_tmpl_id:
            if self.type == 'all':
                res = res.search([('product_tmpl_id', '=', self.product_tmpl_id.id)])
            else:
                products = res.search([('product_tmpl_id', '=', self.product_tmpl_id.id)])
                values = self.product_attribute_value.ids
                for p in products:
                    attribute = p.attribute_value_ids.ids
                    if set(attribute) <= set(values):
                        res += p
        else:
            if self.type == 'all':
                res= res.search([])
            else:
                values = self.product_attribute_value.ids
                products = res.search([])
                for p in products:
                    attribute = p.attribute_value_ids.ids
                    if set(attribute) <= set(values):
                        res += p
        vals = {}
        if self.is_item_fee:
            vals['item_fee'] = self.item_fee
        if self.is_weight_fee:
            vals['weight_fee'] = self.weight_fee
        if self.is_additional_fee:
            vals['additional_fee'] = self.additional_fee
        if self.product_sample_location:
            vals['product_sample_location'] = self.product_sample_location.id
        return res.write(vals)