# -*- coding: utf-8 -*-
'''
Created on 2016年3月3日

@author: cloudy
'''
from openerp import models,fields

class stock_warehouse(models.Model):
    _inherit = 'stock.warehouse'
    
    user_ids = fields.Many2many('res.users','stock_warehouse_user_ref','warehouse_id','user_id',string='users has operation')
    

class stock_picking_type(models.Model):
    _inherit = 'stock.picking.type'
    user_ids = fields.Many2many(related="warehouse_id.user_ids",string='users has operation')
