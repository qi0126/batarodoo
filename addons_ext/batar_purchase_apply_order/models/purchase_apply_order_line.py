#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:purchase_apply_order_line.py
@date:2016/12/1 13:43
"""
from openerp import  models,fields,api
from openerp.exceptions import UserError

class purchase_apply_order_line(models.Model):
    """采购申购单明细"""
    _name = "purchase.apply.order.line"
    STATES = [
        ('draft','draft'),
        ('confirm','confirm'),
        ('cancel','cancel'),
        ('generate','generate purchase order'),
        ('done','done')
    ]
    order_id =fields.Many2one('purchase.apply.order',string='purchase apply order')
    name = fields.Char(string="purchase apply order line name")
    product_id = fields.Many2one('product.product',string='product')
    product_qty = fields.Float(string='product qty',default=1)
    note = fields.Text(string='order line product note',default="")
    state = fields.Selection(string='states',selection=STATES)
    need_check = fields.Boolean(string="need quality check",default=False)
    supplier_id = fields.Many2one('res.partner',string='supplier',domain=[('supplier','=',True)])
    purchase_order_line = fields.Many2one('purchase.order.line',string="purchase order line")
    batch = fields.Boolean(string="batch send",default=False)
    has_supplier = fields.Boolean(string='has supplier',default=False)

    @api.model
    def create(self, vals):
        note = vals.get('note',"")
        if note:
            vals['note'] = note.strip()
        return super(purchase_apply_order_line, self).create(vals)

    @api.onchange('product_id')
    def product_change(self):
        '''判断产品是否有供应商'''
        if self.product_id:
            if self.env['product.supplier'].search([('product_id','=',self.product_id.id)]):
                self.has_supplier = True
            else:
                self.has_supplier = False
                raise UserError(u"该产品没有对应的供应商，请先添加供应商")








