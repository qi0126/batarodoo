#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:purchase_order_line.py
@date:2016/12/8 17:00
"""
from openerp import  models,fields,api

class purchase_order_line(models.Model):
    """"""
    _inherit = 'purchase.order.line'

    need_check = fields.Boolean(string='need check',default=False)
    customer_id = fields.Many2one('res.partner',string='customer')
    order_note = fields.Text(string='order note',default="")