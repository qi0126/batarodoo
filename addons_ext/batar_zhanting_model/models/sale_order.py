# -*- coding: utf-8 -*-

from openerp import models,fields,api

class sale_order(models.Model):
    _inherit = 'sale.order'

    product_sample_location = fields.Many2one('stock.location', string='product sample location')
