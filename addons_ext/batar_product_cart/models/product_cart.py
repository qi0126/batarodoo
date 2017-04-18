# -*- coding:utf-8 -*-
from openerp import api, models, fields

class product_cart(models.Model):
    _name = 'batar.product.cart'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    qty = fields.Integer(string='Product Qty', default=1)
    item_fee = fields.Float(string='Item fee')
    weight_fee = fields.Float(string='Weight fee')
    additional_fee = fields.Float(string='Additional fee')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    product_sample_location = fields.Many2one('stock.location', string='Sample Location')