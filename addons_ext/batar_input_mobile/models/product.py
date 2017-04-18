# -*- coding: utf-8 -*-
from openerp import api, fields, models

class Product(models.Model):
    _inherit = 'product.product'

    double_uom = fields.Boolean(string='Double Uom', default=False)
    sec_uom = fields.Many2one('product.uom', string='Second Uom')