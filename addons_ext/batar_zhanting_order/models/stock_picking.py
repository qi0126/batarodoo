#!/usr/bin/env python
#coding=utf8
'''
Created on 2016/8/23

@author: cloudy
'''

from openerp import models,api


class stockPicking(models.Model):
    ''''''
    _order = 'id desc'
    _inherit = 'stock.picking'

    @api.multi
    def action_delivery_done(self):
        super(stockPicking, self).action_delivery_done()
        for line in self:
            customer_order = self.env['batar.customer.sale'].search([('state','=','process'),('partner_id','=',line.partner_id.id)])
            if customer_order:
                state = [line.state for line in customer_order.line_ids]
                state = list(set(state))
                if state == ['done']:
                    customer_order.write({'state': 'done'})

    @api.multi
    def action_assign(self):
        super(stockPicking,self).action_assign()
        customer_order_line_obj = self.env['customer.sale.line']
        customer_sale_obj = self.env['batar.customer.sale']

        pick_type_id = self.env['stock.picking.type'].with_context(lang='en').search([('name','ilike','Pick')],limit=1).id
        pack_type_id = self.env['stock.picking.type'].with_context(lang='en').search([('name', 'ilike', 'Pack')],limit=1).id
        out_type_id = self.env['stock.picking.type'].with_context(lang='en').search([('name', 'ilike', 'Delivery Orders')],limit=1).id
        for stock_picking in self:
            all_pickings = self.env['stock.picking'].search([('group_id','=',stock_picking.group_id.id)],order='id asc')
            customer_sale = customer_sale_obj.search([('partner_id','=',stock_picking.partner_id.id),('state','=','process')])


            if not customer_sale:
                values = {
                    'name': stock_picking.name,
                    'partner_id': stock_picking.partner_id.id,
                    'state': 'process'
                }
                customer_sale = customer_sale_obj.create(values)
                #获得客户材质信息
                material_price_line = customer_sale.get_customer_material_price(stock_picking.partner_id.id)
                customer_sale.write({'material_price_line':material_price_line})

            customer_sale_lines = customer_sale.line_ids
            customer_sale_products = [line.product_id.id for line in customer_sale_lines]

            move_lines =stock_picking.move_lines
            product_dict = {}
            for move_line in move_lines:
                if move_line.state != 'cancel':
                    product_dict[move_line.product_id.id] = move_line.product_uom_qty
            move_line_products = [line.product_id.id for line in move_lines if line.state != 'cancel']
            need_create_products = [i for i in move_line_products if i not in customer_sale_products]
            need_update_products = [i for i in move_line_products if i in customer_sale_products]

            line_list = []
            pick_ids = [line.id for line in all_pickings if (line.state != 'cancel' and line.picking_type_id.id == pick_type_id)]
            pack_ids = [line.id for line in all_pickings if (line.state != 'cancel' and line.picking_type_id.id == pack_type_id)]
            out_ids =  [line.id for line in all_pickings if  (line.state != 'cancel' and line.picking_type_id.id == out_type_id)]
            for product_id in need_create_products:
                values = {
                    'product_id':product_id,
                    'change_qty':0,
                    'exchange_qty':0,
                }
                if pick_ids:
                    stock_pick_ids =[]
                    for line in pick_ids:
                        stock_pick_ids.append((4, line, None))
                    values['pick_ids'] = stock_pick_ids
                if pack_ids:
                    stock_pack_ids = []
                    for line in pack_ids:
                        stock_pack_ids.append((4, line, None))
                    values['pack_ids'] = stock_pack_ids
                if out_ids:
                    stock_out_ids = []
                    for line in out_ids:
                        stock_out_ids.append((4, line, None))
                    values['out_ids'] = stock_out_ids


                line_list.append((0,0,values))
            if line_list:
                customer_sale.write({
                    'line_ids':line_list
                })
            for product_id in need_update_products:
                customer_order_line =customer_order_line_obj.search([('line_id','=',customer_sale.id),('product_id','=',product_id)])
                line_values = {
                    # 'order_qty': customer_order_line.order_qty + product_dict.get(product_id, 0),
                }
                if pick_ids:
                    stock_pick_ids = []
                    for line in pick_ids:
                        stock_pick_ids.append((4, line, None))
                    line_values['pick_ids'] = stock_pick_ids
                if pack_ids:
                    stock_pack_ids = []
                    for line in pack_ids:
                        stock_pack_ids.append((4, line, None))
                    line_values['pack_ids'] = stock_pack_ids
                if out_ids:
                    stock_out_ids = []
                    for line in out_ids:
                        stock_out_ids.append((4, line, None))
                    line_values['out_ids'] = stock_out_ids
                if line_values:
                    customer_order_line.write(line_values)

