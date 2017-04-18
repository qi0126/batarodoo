# -*- coding: utf-8 -*-
'''
Created on 2016年4月25日

@author: cloudy
'''
from openerp import models,fields,api

class stock_pack_operation(models.Model):
    _inherit = 'stock.pack.operation'
    
    real_time_price_unit = fields.Float(string='real time price unit')
    standard_weight = fields.Float(related='product_id.standard_weight',string="Standard Weight")
    all_weights = fields.Float(string='all line weight')
    item_fee = fields.Float(string="Item Fee")
    weight_fee = fields.Float(string="weight fee")
    additional_fee = fields.Float(string='additional fee')

    @api.model
    def create(self, vals):
        '''
        '''
        picking_id = vals.get('picking_id',None)
        stock_picking_obj  =self.env['stock.picking'].search([('id','=',picking_id)])
        
        product_id = vals.get('product_id',None)
        move_lines = stock_picking_obj.move_lines_related
        for line in move_lines:
            if line.product_id.id == product_id:
                vals['real_time_price_unit'] = line.real_time_price_unit
                vals['standard_weight'] = line.standard_weight
                vals['item_fee'] = line.item_fee
                vals['weight_fee'] = line.weight_fee
                vals['additional_fee'] = line.additional_fee
                vals['all_weights'] = line.all_weights
        return super(stock_pack_operation,self).create( vals)