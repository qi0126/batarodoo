#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:purchase_apply_order.py
@date:2016/12/1 13:43
"""
from openerp import  models,fields,api
from openerp.exceptions import UserError


class purchase_apply_order(models.Model):
    """采购申购单"""
    _name = "purchase.apply.order"
    STATES = [
        ('draft', 'draft'),
        ('confirm', 'confirm'),
        ('cancel', 'cancel'),
        ('generate', 'generate purchase order'),
        ('done', 'done')
    ]

    name = fields.Char(string='purchase apply order name')
    user_id = fields.Many2one('res.users',string="user", default=lambda self:self.env.uid)
    customer_id = fields.Many2one("res.partner",string='customer')
    send_time = fields.Datetime(string='send time')
    order_time = fields.Datetime(string='order time')
    note = fields.Text(string="customer note",default="")
    state = fields.Selection(string='states',selection=STATES,default="draft")
    supplier_id = fields.Many2one('res.partner',string='supplier',domain=[('supplier','=',True)],help="If you choose, all the details are used by the supplier")

    order_line = fields.One2many("purchase.apply.order.line","order_id",string="purchase apply order line",ondelete='cascade',states={'draft': [('readonly', False)]}, readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.apply.order') or '/'
        return super(purchase_apply_order, self).create(vals)
    @api.onchange("supplier_id")
    def supplier_change(self):
        self.ensure_one()
        for line in self.order_line:
            line.supplier_id = self.supplier_id

    @api.multi
    def draft(self):
        self.ensure_one()
        if self.state == 'confirm':
            self.state = 'draft'
            self.order_line.write({'state':'draft'})
    @api.multi
    def confirm(self):
        self.ensure_one()
        if self.state == 'draft':
            self.state = 'confirm'

    def default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        print types[0].id
        return types[0].id

    @api.multi
    def generate_purchase_order(self):
        self.ensure_one()
        if self.state !='confirm':
            raise UserError(_(u"申购单的状态不为确认，不能生成采购单！"))
        purchase_order_obj =self.env['purchase.order']
        purchase_order_line_obj =self.env['purchase.order.line']

        #所有的申购明细都给同一个供应商
        if self.supplier_id:
            #判断是否有该供应商的采购单
            purchase_order = purchase_order_obj.search([('partner_id','=',self.supplier_id.id),('state','=','draft')])
            if purchase_order:
                #判断是否有和申购单一致的采购明细，若有且在草稿状态，增加明细数量
                for line in self.order_line:
                    order_note = (line.note and line.note.strip() )or ""
                    search_list = [('order_id','=',purchase_order.id),('product_id','=',line.product_id.id),('need_check','=',line.need_check),('order_note','=',order_note)]
                    order_line = purchase_order_line_obj.search(search_list)
                    if order_line:
                        order_line.product_qty += line.product_qty
                        line.purchase_order_line = order_line
                    else:
                        #若没有符合要求的采购明细，新建采购明细
                        line.purchase_order_line = purchase_order_line_obj.create({
                                'order_id':purchase_order.id,
                                'product_id':line.product_id.id,
                                'product_qty':line.product_qty,
                                'order_note':order_note,
                            })

            else:
                #如果没有该供应商的采购单，新建采购单
                order_line_values = []
                for line in self.order_line:
                    order_note = (line.note and line.note.strip()) or ""
                    order_line_values.append([(0,0,{
                                'product_id':line.product_id.id,
                                'product_qty':line.product_qty,
                                'order_note':order_note,
                            })])
                purchase_order_obj.create({
                    'date_planned':self.send_time,
                    'partner_id':self.supplier_id.id,
                    'order_line':order_line_values,
                })
        else:
            #若申购单没有
            order_line_values = []
            for line in self.order_line:
                order_note = (line.note and line.note.strip()) or ""
                search_list =[('product_id','=',line.product_id.id),('state','=','draft'),('order_note','=',order_note)]
                if self.customer_id:
                    search_list.append(('customer_id','=',self.customer_id.id))
                order_line = purchase_order_line_obj.search(search_list)
                if order_line:
                    order_line.product_qty += line.product_qty
                    line.purchase_order_line = order_line
                else:
                    order_line_values.append([(0, 0, {
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'order_note': order_note,
                    })])
            if order_line_values:
                picking_type_id = self.default_picking_type()
                purchase_values = {
                    'date_planned': self.send_time,
                    'order_line': order_line_values,
                    'date_order': fields.datetime.now(),
                    'picking_type_id':picking_type_id,
                    'partner_id':1,
                }
                if self.supplier_id:
                    purchase_values['partner_id'] = self.supplier_id.id
                purchase_order_obj.create(purchase_values)


        self.state = 'generate'
        self.order_line.write({'state': 'generate'})






