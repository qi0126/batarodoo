# -*- coding: utf-8 -*-
'''
Created on 2016年5月21日

@author: cloudy
'''
from openerp import models,fields,api
from openerp.exceptions import UserError,ValidationError


class product_category(models.Model):
    _inherit = "product.category"
    
    name= fields.Char('Name', required=True, translate=False, select=True)
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'category name must be unique!'), 
    ]
