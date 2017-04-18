# -*- coding: utf-8 -*-
from openerp import api, fields, models

class BatarWeight(models.Model):
    _name = 'batar.weight'

    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Integer(string='Qty')
    offset_weight = fields.Float(string='Offset Weight')
    ref = fields.Char(string='Ref Order')
    net_weight = fields.Float(string='Net Weight')

class Product(models.Model):
    _inherit = 'product.product'

    support_uom = fields.Boolean(string='Support Uom', default=True)