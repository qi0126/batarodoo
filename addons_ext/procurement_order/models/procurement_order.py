# -*- coding: utf-8 -*-
'''
Created on 2016年3月21日

@author: cloudy
'''
from openerp import models,fields,api

class procurement_order(models.Model):
    _inherit = 'procurement.order'
    
    order_line_id = fields.Many2one('sale.order.line',string='sale order line')
    
    
    @api.model
    def create(self, vals):
        sale_line_id = vals.get('sale_line_id',None)
        if sale_line_id:
            order_line_id = self.env['sale.order.line'].search([('id','=',sale_line_id)])
            if order_line_id:
                vals['order_line_id'] = order_line_id.id     
        return super(procurement_order,self).create(vals)
    