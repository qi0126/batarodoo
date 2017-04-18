# -*- coding: utf-8 -*-
from openerp import api, fields, models, exceptions
import logging
_logger = logging.getLogger(__name__)

class MassProduct_expense(models.TransientModel):
    _name = 'batar.product.expense.tree'

    is_item_fee = fields.Boolean(string="Item fee?", default=False)
    is_weight_fee = fields.Boolean(string='Weight fee?', default=False)
    is_additional_fee = fields.Boolean(string='Additional fee?', default=False)
    item_fee = fields.Float(string='Item fee')
    weight_fee = fields.Float(string='Weight fee')
    additional_fee = fields.Float(string='Additional fee')
    product_sample_location = fields.Many2one('stock.location', string='Sample Location')
    is_active = fields.Boolean(string='Active', default=False)

    @api.multi
    def confirm(self):
        products = self.env['product.product'].browse(self._context.get('active_ids', []))
        vals = {}
        if self.is_item_fee:
            vals['item_fee'] = self.item_fee
        if self.is_weight_fee:
            vals['weight_fee'] = self.weight_fee
        if self.is_additional_fee:
            vals['additional_fee'] = self.additional_fee
        if self.product_sample_location:
            vals['product_sample_location'] = self.product_sample_location.id
        if self.is_active:
            vals['active'] = True
        return products.write(vals)