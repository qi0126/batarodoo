# -*- coding: utf-8 -*-
from openerp import api, models, fields

class product_cart_expense_wizard(models.TransientModel):
    _name = 'batar.product.cart.expense.wizard'
    _inherit = 'batar.product.expense.tree'

    @api.multi
    def confirm(self):
        orders = self.env['batar.product.cart'].browse(self._context.get('active_ids', []))
        res = self.env['product.product']
        vals = {}
        for line in orders:
            res += line.product_id
        if self.is_item_fee:
            vals['item_fee'] = self.item_fee
        if self.is_weight_fee:
            vals['weight_fee'] = self.weight_fee
        if self.is_additional_fee:
            vals['additional_fee'] = self.additional_fee
        if self.product_sample_location:
            vals['product_sample_location'] = self.product_sample_location.id
        res.write(vals)
        orders.unlink()
        return True