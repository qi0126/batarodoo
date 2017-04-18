# -*- coding: utf-8 -*-
'''
Created on 2016年2月29日

@author: cloudy
'''
from openerp import models,fields,api


class stock_move(models.Model):
    _inherit = 'stock.move'
    
   
    order_line_id = fields.Many2one(related='procurement_id.order_line_id',string='sale order line')
    real_time_price_unit = fields.Float(related='order_line_id.real_time_price_unit',string='real time price unit')
    standard_weight = fields.Float(related='order_line_id.standard_weight',string="Standard Weight")
    all_weights = fields.Float(string='all line weight')
    item_fee = fields.Float(related='order_line_id.item_fee',string="Item Fee")
    weight_fee = fields.Float(related='order_line_id.weight_fee',string="weight fee")
    additional_fee = fields.Float(related='order_line_id.additional_fee',string='additional fee') 
    ponderable = fields.Boolean(related='product_id.ponderable',string="ponderable")
    price_subtotal = fields.Float(string='sub total')
    
#     @api.v8
#     @api.onchange('all_weights')
#     def sale_change(self):
#         ''''''
#         if self.order_line_id:
#             self.order_line_id.all_weights = self.all_weights
                
    @api.model
    def create(self, vals):
#         order_line_id = vals.get('order_line_id','')
#         if order_line_id:
#             vals['item_fee'] = order_line_id.item_fee
#             vals['weight_fee'] = order_line_id.weight_fee
#             vals['all_weights'] = order_line_id.all_weights
        procurement_id = vals.get('procurement_id',None)
        if procurement_id:
            procurement = self.env['procurement.order'].search([('id','=',procurement_id)])
            if procurement:
                vals['item_fee'] = procurement.order_line_id.item_fee
                vals['weight_fee'] = procurement.order_line_id.weight_fee
                vals['all_weights'] = procurement.order_line_id.all_weights
        restrict_partner_id = vals.get('restrict_partner_id',None)
        if restrict_partner_id:
            vals['restrict_partner_id'] =restrict_partner_id.id
        return super(stock_move,self).create(vals)
    
    
    # @api.multi
    # def write(self, vals):
    #     product_uom_qty = vals.get('product_uom_qty',0)
    #     if product_uom_qty:
    #         self.procurement_id.write({'product_qty':product_uom_qty})
    #         self.order_line_id.write({'product_uom_qty':product_uom_qty})
    #     return super(stock_move,self).write( vals)

