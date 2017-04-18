# -*- coding: utf-8 -*-

from openerp import models, fields, api,_
from openerp.exceptions import UserError


class quality_order(models.Model):
    '''质量检测单'''
    _name = "quality.order"
    _order = 'id desc'

    _STATE =[
        ('draft','draft'),
        ('confirm','confirm'),
        ('wait_check','wait check'),
        ('partal','gen pick in'),
        ('done','done')
    ]

    name = fields.Char(string='quality order name')
    line_ids = fields.One2many('quality.order.line','quality_id',string='quality order line')
    check_ids = fields.One2many('quality.order.check.record', 'quality_id', string='quality order check record')
    check_user = fields.Many2one('res.users',string='quality checker')
    partner_id = fields.Many2one('res.partner', store=True, string='partner')
    partner_person = fields.Char(string='supplier charge man')
    partner_mobile = fields.Char(string='supplier charge man mobile')
    delivery_method = fields.Char(string='delivery method')
    delivery_man = fields.Char(string='delivery charge man')
    delivery_mobile = fields.Char(string='delivery charge man mobile')
    state = fields.Selection(_STATE, string='state', default='draft')
    location_src_id = fields.Many2one('stock.location', string='source location')
    location_dest_id = fields.Many2one('stock.location', string='dest location')

    @api.multi
    def gen_picking_in_order(self):
        """生成待分拣单"""

        for quality_order in self:
            must_check_state = [str(line.state) for line in quality_order.line_ids if line.must_check]
            must_check_state = list(set(must_check_state))
            print 'must_check_state',":",must_check_state
            if must_check_state and must_check_state != ['checked']:
                raise UserError(_(u"有必检的明细没有检测"))
            quality_back_order_line_values = []
            pick_in_order_line_values = []
            for order_line in quality_order.line_ids:
                if not order_line.ok:
                    quality_back_order_line_values.append((0,0,{
                        'supplier_code':order_line.supplier_code,
                        'default_code':order_line.default_code,
                        'product_id':order_line.product_id.id,
                        'product_qty':order_line.product_qty,
                        'net_weight':order_line.net_weight,
                        'gross_weight':order_line.gross_weight,
                        'check_user':order_line.check_user.id,
                    }))
                    continue
                pick_in_order_line_values.append((0,0,{
                    'name': order_line.name,
                    'default_code': order_line.default_code,
                    'product_id': order_line.product_id.id,
                    'product_qty': order_line.product_qty,
                    'net_weight': order_line.net_weight,
                    'gross_weight': order_line.gross_weight,
                    'actual_product_qty': order_line.product_qty,
                    'actual_net_weight': order_line.net_weight,
                    'actual_gross_weight': order_line.gross_weight,
                    'state': 'wait_split',
                    'method': quality_order.delivery_method,
                    'quality_id': quality_order.id,
                }))
                order_line.state = 'done'
                order_line.ok = True

            if pick_in_order_line_values:
                self.env['stock.pick.in.order'].create({
                    'line_ids': pick_in_order_line_values,
                    'check_user': self.env.uid,
                    #加入调拨方式到分拣单
                    'method': quality_order.delivery_method,
                })
            if quality_back_order_line_values:
                quality_back_order_values = {

                    'supplier':quality_order.partner_id.id,
                    'quality_id':quality_order.id,
                    'line_ids':quality_back_order_line_values,
                }
                self.env['quality.back.order'].create(quality_back_order_values)
            quality_order.state = 'done'



class quality_order_line(models.Model):
    '''质检明细'''
    _name = "quality.order.line"
    _STATE = [
        ('draft', 'draft'),
        ('confirm', 'confirm'),
        ('wait_check', 'wait check'),
        ('checked','checked'),
        ('done', 'done')
    ]

    name = fields.Char(string='package number')
    quality_id = fields.Many2one('quality.order',ondelete='cascade',string='quality order name')
    supplier_code = fields.Char(string='supplier code')
    default_code = fields.Char(string='default code')
    product_id = fields.Many2one('product.product', string='product')
    product_qty = fields.Float(string='product quantity')
    net_weight = fields.Float(string='net weight')
    gross_weight = fields.Float(string='gross weight')
    ok = fields.Boolean(string='pass',default=True)
    state = fields.Selection(_STATE, string='state', default='draft')
    must_check = fields.Boolean(default=False,string='must check')
    check_record = fields.One2many('quality.order.check.record', 'order_line_id', string='quality order check record')
    check_user = fields.Many2one('res.users', string='quality checker')


class quality_order_check_record(models.Model):
    '''质检记录'''
    _name = 'quality.order.check.record'

    check_user = fields.Many2one('res.users', string='quality checker')
    quality_id = fields.Many2one('quality.order', string='quality order name')
    order_line_id = fields.Many2one("quality.order.line",string="quality order line")
    supplier_code = fields.Char(string='supplier code')
    default_code = fields.Char(string='default code')
    product_id = fields.Many2one('product.product', string='product')
    product_qty = fields.Float(string='product quantity')
    net_weight = fields.Float(string='net weight')
    gross_weight = fields.Float(string='gross weight')
    ok = fields.Boolean(string='pass', default=False)
    reason = fields.Many2one("quality.reason", string="reason")


class quality_reason(models.Model):
    '''质检不通过的原因'''
    _name = 'quality.reason'
    name = fields.Char(string='quality reason')


