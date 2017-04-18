# -*- coding: utf-8 -*-
'''
Created on 2016年5月28日

@author: cloudy
'''
from openerp import fields,models

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    pkg_name = fields.Char(string='package name')