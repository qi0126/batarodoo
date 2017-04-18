# -*- coding: utf-8 -*-
'''
Created on 2016年7月4日

@author: cloudy
'''
from openerp.osv import fields, osv

class sale_configuration(osv.TransientModel):
    _inherit = 'sale.config.settings'
    _columns = {
        'lock_time':fields.float("sale order stock lock time"),
    }
    _defaults ={
        'lock_time':2,
    }