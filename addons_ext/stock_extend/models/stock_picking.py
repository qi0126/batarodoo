# -*- coding: utf-8 -*-
'''
Created on 2016年4月25日

@author: cloudy
'''
from openerp import models,fields,api
from openerp.tools import float_compare

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
#     order_id = fields.Many2one('sale.order',string='sale order')
#     purchase_id =fields.Many2one('purchase.order',string='purchase order')
#     
#     @api.model
#     def create(self, vals):
#         origin = vals.get('origin',None)
#         if origin:
#             sale_obj = self.env['sale.order'].search([('name','=',origin)])
#             if sale_obj:
#                 vals['order_id'] = sale_obj.id
#             purchase_obj = self.env['purchase.order'].search([('name','=',origin)])
#             if purchase_obj:
#                 vals['purchase_id'] = purchase_obj.id
#         return super(stock_picking,self).create(vals)
    
    @api.multi
    def write(self, vals):
        pack_operation_product_ids = vals.get('pack_operation_product_ids',[])
        for stock_picking_line in self:
            for line in pack_operation_product_ids:
                if type(line) == type([]):
                    if len(line) == 3:
                        if type(line[2]) == type({}):
                            all_weights = line[2].get("all_weights",0)
                            if all_weights:
                                operation = self.env['stock.pack.operation'].search([('id','=',line[1])])
                                move_lines = self.env['stock.move'].search([('picking_id','=',stock_picking_line.id)])
                                for move_line in move_lines:
                                    if move_line.product_id.id == operation.product_id.id:
                                        move_line.all_weights = all_weights
                                        move_line.order_line_id.all_weights = all_weights                 
        return super(stock_picking,self).write(vals)
                