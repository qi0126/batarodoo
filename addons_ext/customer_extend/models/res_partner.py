# -*- coding: utf-8 -*-
'''
Created on 2016年1月15日

@author: cloudy
'''

from openerp import fields, models 

class res_partner(models.Model):
    _inherit = 'res.partner'
    # customer_code = fields.Char(string='customer code')
    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'客户名称必须唯一!'),
    ]
