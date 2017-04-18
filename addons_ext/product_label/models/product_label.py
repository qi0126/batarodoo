# -*- coding: utf-8 -*-
'''
Created on 2016年6月3日

@author: cloudy
'''
from openerp import models,fields
class product_label(models.TransientModel):
    _name ='product.label'
    product_id = fields.Many2one('product.product',string='product')
    weight = fields.Float(string='product weight')
    