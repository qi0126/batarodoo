#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:stock_pick_in.py
@date:2016/12/10 13:32
"""
from openerp import models, api, fields


class stock_pick_in_order(models.Model):
    """质检通过后的记录"""
    _order = 'id desc'
    _name = 'stock.pick.in.order'
    _STATE = [
        ('wait_split', 'wait_split'),
        ('wait_pick_in', 'wait_pick_in'),
        ('done', 'done')
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.pick.in.order') or '/'
        return super(stock_pick_in_order, self).create(vals)

    name = fields.Char(string='stock pick in order')
    line_ids = fields.One2many('stock.pick.in.order.line', 'order_id', string='stock pick in order line')
    check_user = fields.Many2one('res.users', string='quality checker')
    state = fields.Selection(_STATE, string='state', default='wait_split')
    # 加入调拨方式到分拣单
    method = fields.Char(string='Picking Type')


class stock_pick_in_order_line(models.Model):
    """待分拣入库明细"""
    _name = 'stock.pick.in.order.line'

    _STATE = [
        ('wait_split', 'wait_split'),
        ('wait_pick_in', 'wait_pick_in'),
        ('done', 'done')
    ]
    name = fields.Char(string='package number')
    order_id = fields.Many2one('stock.pick.in.order', ondelete='cascade', string='stock pick in order')
    default_code = fields.Char(string='default code')
    product_id = fields.Many2one('product.product', string='product')
    product_qty = fields.Float(string='product quantity')
    net_weight = fields.Float(string='net weight')
    gross_weight = fields.Float(string='gross weight')
    actual_product_qty = fields.Float(string='actual product quantity')
    actual_net_weight = fields.Float(string='actual net weight')
    actual_gross_weight = fields.Float(string='actual gross weight')
    state = fields.Selection(_STATE, string='state', default='wait_split')
    plate_id = fields.Many2one('quality.plate', string='quality plate')
    sequence = fields.Integer(string='sequence')
    method = fields.Char(string='Picking Type')
    quality_id = fields.Many2one('quality.order', string='Quality order')

    @api.multi
    def write(self, vals):
        """"""
        # state = vals.get('state','')
        # if state =='done':
        #     for order_line in self:
        #         order = self.env['stock.pick.in.order.line'].search([('order_id','=',order_line.order_id.id),('state','=','wait_pick_in')])
        #         if order and len(order) == 1:
        #             if order.id == order_line.id:
        #                 order_line.order_id.state = 'done'
        # return super(stock_pick_in_order_line, self).write(vals)
        res = super(stock_pick_in_order_line, self).write(vals)
        for order_line in self:
            orders = self.env['stock.pick.in.order.line'].search([('order_id', '=', order_line.order_id.id)])
            if all([a.state == 'done' for a in orders]):
                order_line.order_id.state = 'done'
            elif all([a.state == 'wait_pick_in' for a in orders]):
                order_line.order_id.state = 'wait_pick_in'
            elif all([a.state == 'wait_split' for a in orders]):
                order_line.order_id.state = 'wait_split'
            else:
                order_line.order_id.state = 'wait_pick_in'
        return res


class quality_plate(models.Model):
    _name = 'quality.plate'
    _order = "id desc"
    _STATE = [
        ('draft', 'draft'),
        ('wait_pick_in', 'wait_pick_in'),
        ('wait_split', "wait split"),
        ('pick_done', 'pick done')
    ]
    user_id = fields.Many2one('res.users', default=lambda self: self.env.uid, string='pick in order weigh user')
    name = fields.Char(string='plate name')
    line_ids = fields.One2many('stock.pick.in.order.line', 'plate_id', string='stock pick in order line')
    state = fields.Selection(_STATE, string='state', default='draft')

    @api.multi
    def write(self, vals):
        """检测分盘状态改变"""
        state = vals.get('state', "")
        if state == 'pick_done':
            self.line_ids.write({'state': 'done'})
        return super(quality_plate, self).write(vals)
