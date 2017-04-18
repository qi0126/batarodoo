#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:quality_back_order.py
@date:2016/12/14 9:49
"""
from openerp import  models,fields,api

class quality_back_order(models.Model):
    """质检退货"""
    _name = 'quality.back.order'
    _STATE = [
        ('draft', 'draft'),
        ('confirm', 'confirm'),
        ('return', 'return back'),
        ('done', 'done')
    ]
    name = fields.Char(string='quality back order')
    line_ids = fields.One2many('quality.back.order.line','order_id',string='quality back order line')
    supplier = fields.Many2one('res.partner',domain=[('supplier','=',True)])
    quality_id = fields.Many2one('quality.order', string='quality back order')
    state = fields.Selection(_STATE,string='state',default='draft')

    @api.multi
    def confirm(self):
        self.write({'state':'confirm'})

    @api.multi
    def action_return(self):
        self.write({'state': 'return'})

    @api.multi
    def done(self):
        self.write({'state': 'done'})
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('quality.back.order') or '/'
        return super(quality_back_order, self).create(vals)


class quality_back_order_line(models.Model):
    """质检退货明细"""
    _name = 'quality.back.order.line'
    order_id = fields.Many2one('quality.back.order',string='quality back order')
    supplier_code = fields.Char(string='supplier code')
    default_code = fields.Char(string='default code')
    product_id = fields.Many2one('product.product', string='product')
    product_qty = fields.Float(string='product quantity')
    net_weight = fields.Float(string='net weight')
    gross_weight = fields.Float(string='gross weight')
    check_user = fields.Many2one('res.users', string='check user')
