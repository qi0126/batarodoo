# -*- coding: utf-8 -*-
'''
Created on 2016年7月23日

@author: cloudy
'''

from openerp import models,fields,api
from openerp.exceptions import UserError


class stock_pick_add(models.Model):
    _name = 'stock.pick.add'
    _order = "id desc"
    
    PRIORITIES = [('0', 'Not urgent'), ('1', 'Normal'), ('2', 'Urgent'), ('3', 'Very Urgent')]
    STATES = [('draft','draft'),('cancel','cancel'),('confirm','confirm'),('done','done')]
    
    
    origin = fields.Char(string='origin',default="")
    name = fields.Char(string='stock pick add name')
    partner_id = fields.Many2one('res.partner',string='partner')
    warehouse_id = fields.Many2one('stock.warehouse',string='ware house',default= lambda self:self.env['ir.model.data'].get_object_reference('stock', 'warehouse0')[1])
    location_id = fields.Many2one('stock.location',string='stock location', default= lambda self:self.env['ir.model.data'].get_object_reference('stock', 'stock_location_customers')[1])
    date_planed = fields.Datetime(string='date planned',default=lambda self: fields.Datetime.now())
    priority = fields.Selection(PRIORITIES,string='priority',default='2')
    state = fields.Selection(STATES,string='states',default='draft')
    add_lines = fields.One2many('stock.pick.add.line','add_id', string='stock pick add lines')
    group_id = fields.Many2one('procurement.group',string='procurement group')
    delivery_count = fields.Integer(compute="_get_delivery_count",string='delivery count')
    product_sample_location = fields.Many2one('stock.location', string='product sample location')
     
    @api.one
    @api.depends('group_id')
    def _get_delivery_count(self):
        ''''''
        if self.group_id:
            picking_list = self.env['stock.picking'].search([('group_id','=',self.group_id.id)])
            self.delivery_count = len(picking_list)
        else:
            self.delivery_count
    
    @api.multi
    def return_draft(self):
        self.ensure_one()
        self.state = "draft"
        self.add_lines.write({'state':'draft'})
        
    @api.multi
    def cancel(self):
        self.ensure_one()
        if self.state in ('draft','confirm'):
            self.state = "cancel"
        else:
            raise UserError(u"非草稿和确认状态下的单据不能取消")
        self.add_lines.write({'state':'cancel'})
    
    @api.multi
    def unlink(self):
        self.ensure_one()
        if self.state  not in ('draft','confirm'):
            raise UserError(u"非草稿和确认状态下的单据不能删除")
        else:
            return super(stock_pick_add, self).unlink()
        
    @api.multi
    def confirm(self):
        ''''''
        self.ensure_one()
        self.state = "confirm"
        self.add_lines.write({'state':'confirm'})
    
    @api.multi
    def generate_pick_pack_out(self):
        ''''''
        self.ensure_one()
        #生成需求组
        group_vals = {
            'name':self.name,
            'move_type':'direct',
            'partner_id':self.partner_id.id 
        }
        
        pro_group = self.env['procurement.group'].create(group_vals)
        self.group_id = pro_group.id
        for line in self.add_lines:
            values = {
                'product_id':line.product_id.id,
                'product_qty':line.product_qty,
                'product_uom':line.product_id.uom_id.id,
                'warehouse_id' :self.warehouse_id.id,
                'location_id':self.location_id.id,
                'date_planed' :self.date_planed,
                'priority':self.priority,
                'name':line.product_id.name,
                'group_id':pro_group.id,
                'origin':self.name,
                'partner_dest_id':self.partner_id.id
            }
            procurement = self.env['procurement.order'].create(values)
            procurement.run()
        stock_pickings = self.env['stock.picking'].search([('group_id','=',pro_group.id)],order='id',limit=1)
#         if stock_picking:
#             print stock_picking.action_assign()
            
        for line in stock_pickings:
            line.action_assign()
        self.state = "done"
        self.add_lines.write({'state':'done'})
        
            
             
    @api.onchange('origin')
    def change_origin(self):
        if self.origin and self.partner_id:
            self.origin = str(self.origin).strip()
            pick_list = self.env['stock.pick.add'].search([('partner_id', '=', self.partner_id), ('origin','=',self.origin),('state','=','draft')])
            if  pick_list:
                mesg = u"%s该销售订单存在草稿状态的补货单，请在“%s”该单据中增加" %(self.origin,pick_list[0].name)
                raise UserError(mesg)
            pick_list = self.env['stock.pick.add'].search([('origin','=',self.origin)],order="id desc",limit=1)
            if pick_list:
                
                name  = pick_list[0].name

                index = name.split("A")[1]
                name_suffix = int(index)+1
                self.name = "%sA%s"% (self.origin,name_suffix)
            else:
                self.name = "%sA1"% self.origin
    @api.multi
    def go_stock_picking(self):
        ''''''
        picking_list = self.env['stock.picking'].search([('group_id','=',self.group_id.id)])
        action = self.env.ref('stock.action_picking_tree_all')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }

        pick_ids = [line.id for line in picking_list]

        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',["+','.join(map(str, pick_ids))+"])]"
        elif len(pick_ids) == 1:
            form = self.env.ref('stock.view_picking_form', False)
            form_id = form.id if form else False
            result['views'] = [(form_id, 'form')]
            result['res_id'] = pick_ids[0]
        return result
    
class stock_pick_add_line(models.Model):
    _name = 'stock.pick.add.line'
    
    STATES = [('draft','draft'),('cancel','cancel'),('confirm','confirm'),('done','done')]
    
    
    
    add_id = fields.Many2one('stock.pick.add',ondelete='cascade',string='stock pick add')
    product_id = fields.Many2one('product.product',string='product')
    product_qty= fields.Float(string='product qty',default=1.0)         
    state = fields.Selection(STATES,string='states',default='draft')
    _sql_constraints = [
        ('add_line_product', 'unique(product_id, add_id)', 'product must be unique per order!'),
    ]
    
    
    @api.onchange('product_id','product_qty')
    def product_change(self):
        ''''''
        if self.product_id:
            if int(self.product_id.virtual_available) <int(self.product_qty):

                mesg = u"“%s(%s)”库存不足，只有%s,请修改数量或者选择别的产品" %(self.product_id.default_code,self.product_id.name,self.product_id.virtual_available)
                raise UserError(mesg)


    
    