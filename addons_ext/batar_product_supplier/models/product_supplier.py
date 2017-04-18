#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:product_supplier.py
@date:2016/11/1 14:34
"""
from  openerp import models,api,fields
import openerp.addons.decimal_precision as dp

class product_supplier(models.Model):
    '''规格产品供应商'''
    _name = "product.supplier"
    _order = 'sequence'

    name = fields.Many2one("res.partner",string='supplier')
    product_id = fields.Many2one('product.product',string='product')
    supplier_product_code = fields.Char(string='supplier product code')
    supplier_product_name = fields.Char(string='supplier product name')
    product_uom = fields.Many2one(related='product_id.uom_id',string=u'单位')
    # uom_id = fields.Many2one(related='product_id.uom_id', string='product uom')
    min_qty = fields.Float(string='min order quantity')
    sequence = fields.Integer(string='supplier sequence')
    price = fields.Float(string='Price', required=True, digits_compute=dp.get_precision('Product Price'),
                         help="The price to purchase a product", default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self:self.env.user.company_id.currency_id)
    delay = fields.Integer(string='Delivery Lead Time', required=True, default=1)

    _sql_constraints = [
        ('unique', 'unique(name, product_id)', u'供应商必须唯一！'),
    ]


class product_product(models.Model):
    '''产品规格'''
    _inherit = 'product.product'
    supplier_info = fields.One2many('product.supplier', 'product_id', string='supplier info')
