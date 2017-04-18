#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:batar_delivery_bill.py
@date:2016/10/31 16:16
"""
from openerp import models,api

class batar_delivery_bill(models.Model):
    """"""
    _inherit = "delivery.bill"


    @api.multi
    def generate_check_order(self):
        """生成质检单"""
        for order in self:
            order_values = {}
            order_values['name'] = order.name
            order_values['partner_id'] = order.partner_id.id
            order_values['partner_person'] = order.partner_person
            order_values['partner_mobile'] = order.partner_mobile
            order_values['delivery_method'] = order.delivery_method
            order_values['delivery_man'] = order.delivery_man
            order_values['delivery_mobile'] = order.delivery_mobile
            order_values['location_src_id'] = order.location_src_id.id
            order_values['location_dest_id'] = order.location_dest_id.id
            order_values['state'] = 'wait_check'
            line_values =[]
            for order_line in order.line_id:
                line_values.append((0,0,{
                    'name':order_line.name,
                    'supplier_code':order_line.supplier_code,
                    'default_code':order_line.default_code,
                    'product_id':order_line.product_id.id,
                    'product_qty':order_line.product_qty,
                    'net_weight':order_line.net_weight,
                    'gross_weight':order_line.gross_weight,
                    'must_check':order_line.must_check,
                    'state':'wait_check',
                }))
            order_values['line_ids'] = line_values
            if self.env['quality.order'].create(order_values):
                order.state = 'check'
                order.line_id.write({'state':'check'})