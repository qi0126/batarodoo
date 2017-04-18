# -*- coding: utf-8 -*-

from openerp import models,fields

class product_category(models.Model):
    _inherit = 'product.category'
    top_cate = fields.Boolean(string='top cate',default=False)