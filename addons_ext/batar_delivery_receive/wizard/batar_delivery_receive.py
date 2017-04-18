# -*- coding: utf-8 -*-
'''
Created on 2016年5月24日

@author: cloudy
'''
from openerp import models,fields,api
from openerp.exceptions import UserError



class delivery_receive(models.TransientModel):
    _name='delivery.receive'
    
    def _default_src_location(self):
        '''默认库位'''
        obj = self.env['stock.picking.type'].search([('code','=','incoming')])
        if len(obj)==1:
            return obj.default_location_src_id.id
        else:
            return None
        
    def _default_dest_location(self):
        '''默认库位'''
        obj = self.env['stock.picking.type'].search([('code','=','incoming')])
        if len(obj)==1:
            return obj.default_location_dest_id.id
        else:
            return None

    @api.one
    @api.depends('pkg_number')
    def _default_location(self):
        ''''''
        bill_line = self.env['delivery.bill.line'].search(['|',('pkg_number','=',self.pkg_number),('parent_pkg_number','=',self.pkg_number)],limit=1)
        if bill_line:
            self.location_src_id = bill_line.delivery_id.location_src_id
            self.location_dest_id = bill_line.delivery_id.location_dest_id
    
    _STATE = [
        ('draft','draft'),
        ('info','info'),
        ('confirm','confirm'),
        ('fail','failed')
    ]  
    pkg_number = fields.Char(string='package number')
    location_src_id = fields.Many2one('stock.location',compute='_default_location',string='stock location source')
    location_dest_id = fields.Many2one('stock.location',compute='_default_location',string='stock location dest')
    receive_lines = fields.One2many('delivery.receive.line','bill_line',string='delivery bill line')
    state = fields.Selection(_STATE,string='delivery receive state')
    info = fields.Char(string='warning message')
    delivery_dest_lines = fields.One2many('delivery.dest.location.line','bill_line',string='delivery dest location line')
    is_sample = fields.Boolean(string="Is sample", default=False)
    _defaults ={
        'state':'draft',
    }

    @api.onchange('pkg_number')
    def onchange_sample(self):
        bill_line = self.env['delivery.bill.line'].search(
            ['|', ('pkg_number', '=', self.pkg_number), ('parent_pkg_number', '=', self.pkg_number)], limit=1)
        if bill_line:
            if bill_line.delivery_id.location_dest_id.putaway_strategy_id.method == 'semi_auto':
                self.is_sample = True

    @api.multi
    def delivery_receive_refuse(self):
        self.ensure_one()
        delivery_bill_line = self.env['delivery.bill.line'].search(["|",('parent_pkg_number','=',self.pkg_number),('pkg_number','=',self.pkg_number)],limit=1)
        if delivery_bill_line:
            delivery_bill_line.state = 'refuse'
            delivery_bill_line.delivery_id.state='error'
    @api.multi
    def delivery_samplelocation(self):
        self.ensure_one()
        stock_picking_obj = self.env['stock.picking']
        delivery_dest_line_ids = []
        # limit为1，只为获得包的目标和源库位，以及客户信息
        delivery_bill_line = self.env['delivery.bill.line'].search(
            ["|", ('parent_pkg_number', '=', self.pkg_number), ('pkg_number', '=', self.pkg_number)], limit=1)
        delivery_bill_name = ''
        if delivery_bill_line:
            delivery_bill_name = delivery_bill_line.delivery_id.name
        if not delivery_bill_name:
            raise UserError(u"包：‘%s’对应的送货单号不存在")

        # 每包创建一个送货单
        for receive_line in self.receive_lines:
            stock_picking_order = stock_picking_obj.search([('pkg_name', '=', receive_line.name)])
            # 更新送货单明细中的实际重量和数量信息
            bill_line = self.env['delivery.bill.line'].search([('pkg_number', '=', receive_line.pkg_number)], limit=1)
            if bill_line:
                bill_line.actual_product_qty = receive_line.actual_product_qty
                bill_line.actual_net_weight = receive_line.actual_net_weight
            if not delivery_bill_line.product_id.product_sample_location.id:
                raise UserError(u"请设置此产品的样品库")
            else:
                values = {
                    'pkg_name': receive_line.name,
                    'partner_id': delivery_bill_line.delivery_id.partner_id.id,
                    'location_id': delivery_bill_line.delivery_id.location_src_id.id,
                    'location_dest_id': delivery_bill_line.product_id.product_sample_location.id,
                    'move_type': 'one',
                    'state': 'draft',
                    'picking_type_id': 1,
                    'move_lines': [(0, 0, {
                        'state': 'draft',
                        'product_id': receive_line.product_id.id,
                        'product_uom': receive_line.product_id.uom_id.id,
                        'product_uom_qty': receive_line.actual_product_qty,
                        'all_weights': receive_line.actual_net_weight,
                        'second_uom': receive_line.actual_net_weight,
                        'location_id': delivery_bill_line.delivery_id.location_src_id.id,
                        'location_dest_id': delivery_bill_line.product_id.product_sample_location.id,
                        'name': receive_line.pkg_number,
                    })]
                }
                # 创建入库单
                stock_picking_id = stock_picking_obj.create(values)
                # 入库单确认
                stock_picking_id.action_confirm()

                pack_operations = self.env['stock.pack.operation'].search([('picking_id', '=', stock_picking_id.id)])
                location_line = []
                for pack_operation in pack_operations:
                    # 接收的数量
                    pack_operation.qty_done = pack_operation.product_qty
                    # 接收的重量
                    pack_operation.all_weights = receive_line.net_weight
                    # 获得目标库位明细信息
                    #                 dest_line = self.env['delivery.dest.location.line'].create({
                    #                     'location_id':pack_operation.location_dest_id.id,
                    #                     'product_id':pack_operation.product_id.id,
                    #                     'product_qty':pack_operation.product_qty,
                    #                     'net_weight':receive_line.actual_net_weight,
                    #                 })
                    location_line.append((0, 0, {
                        'location_id': pack_operation.location_dest_id.id,
                        'product_id': pack_operation.product_id.id,
                        'product_qty': pack_operation.product_qty,
                        'net_weight': receive_line.actual_net_weight,
                    }))
                    #                 if dest_line:
                    #                     delivery_dest_line_ids.append(dest_line.id)
                show_id = self.env['delivery.dest.location'].create({'line_ids': location_line})
                if show_id:
                    show_id = show_id.id
                # 触发确认收货按钮
                stock_picking_id.do_new_transfer()
                # 更改送货单明细的状态
                bill_lines = self.env['delivery.bill.line'].search([('pkg_number', '=', receive_line.pkg_number)])
                if bill_lines:
                    bill_lines.write({'state': 'confirm'})
                for line in bill_lines:
                    delivery_id = line.delivery_id
                    delivery_bill_lines = self.env['delivery.bill.line'].search([('delivery_id', '=', delivery_id.id)])

                    state = list(set([l.state for l in delivery_bill_lines]))

                    if len(state) == 1:
                        if state[0] == 'confirm':
                            delivery_id.state = 'confirm'
        self.delivery_dest_lines = delivery_dest_line_ids

        return {
            'res_id': show_id,
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'delivery.dest.location',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def delivery_receive_confirm(self):
        self.ensure_one()  
        stock_picking_obj =self.env['stock.picking']
        delivery_dest_line_ids = []
        #limit为1，只为获得包的目标和源库位，以及客户信息
        delivery_bill_line = self.env['delivery.bill.line'].search(["|",('parent_pkg_number','=',self.pkg_number),('pkg_number','=',self.pkg_number)],limit=1)
        delivery_bill_name = ''
        if delivery_bill_line:
            delivery_bill_name = delivery_bill_line.delivery_id.name
        if not delivery_bill_name:
            raise UserError(u"包：‘%s’对应的送货单号不存在")
        
        #每包创建一个送货单    
        for receive_line in self.receive_lines:
            stock_picking_order = stock_picking_obj.search([('pkg_name','=',receive_line.name)])
            #更新送货单明细中的实际重量和数量信息
            bill_line = self.env['delivery.bill.line'].search([('pkg_number','=',receive_line.pkg_number)],limit=1)
            if bill_line:
                bill_line.actual_product_qty = receive_line.actual_product_qty
                bill_line.actual_net_weight = receive_line.actual_net_weight
            values = {
                'pkg_name':receive_line.name,
                'partner_id':delivery_bill_line.delivery_id.partner_id.id,
                'location_id':delivery_bill_line.delivery_id.location_src_id.id,
                'location_dest_id':delivery_bill_line.delivery_id.location_dest_id.id,
                'move_type':'one',
                'state':'draft',
                'picking_type_id':1,
                'move_lines':[(0,0,{
                    'state':'draft',
                    'product_id':receive_line.product_id.id,
                    'product_uom':receive_line.product_id.uom_id.id,
                    'product_uom_qty':receive_line.actual_product_qty,
                    'all_weights':receive_line.actual_net_weight,
                    'second_uom':receive_line.actual_net_weight,
                    'location_id':delivery_bill_line.delivery_id.location_src_id.id,
                    'location_dest_id':delivery_bill_line.delivery_id.location_dest_id.id,
                    'name':receive_line.pkg_number,
                    })]
                }
            #创建入库单
            stock_picking_id = stock_picking_obj.create(values)
            #入库单确认
            stock_picking_id.action_confirm()
             
            pack_operations = self.env['stock.pack.operation'].search([('picking_id','=',stock_picking_id.id)])
            location_line =[]
            for pack_operation in pack_operations:
                #接收的数量
                pack_operation.qty_done = pack_operation.product_qty
                #接收的重量
                pack_operation.all_weights = receive_line.net_weight
                #获得目标库位明细信息
#                 dest_line = self.env['delivery.dest.location.line'].create({
#                     'location_id':pack_operation.location_dest_id.id,
#                     'product_id':pack_operation.product_id.id,
#                     'product_qty':pack_operation.product_qty,
#                     'net_weight':receive_line.actual_net_weight,
#                 })
                location_line.append((0,0,{
                    'location_id':pack_operation.location_dest_id.id,
                    'product_id':pack_operation.product_id.id,
                    'product_qty':pack_operation.product_qty,
                    'net_weight':receive_line.actual_net_weight,
                }))
#                 if dest_line:
#                     delivery_dest_line_ids.append(dest_line.id)
            show_id = self.env['delivery.dest.location'].create({'line_ids':location_line})
            if show_id:
                show_id = show_id.id
            #触发确认收货按钮
            stock_picking_id.do_new_transfer()
            #更改送货单明细的状态
            bill_lines = self.env['delivery.bill.line'].search([('pkg_number','=',receive_line.pkg_number)])
            if bill_lines:
                bill_lines.write({'state':'confirm'})
            for line in bill_lines:
                delivery_id = line.delivery_id
                delivery_bill_lines = self.env['delivery.bill.line'].search([('delivery_id','=',delivery_id.id)])
               
                state = list(set([l.state for l in delivery_bill_lines]))
               
                if len(state) ==1:
                    if state[0] == 'confirm':
                        delivery_id.state = 'confirm'
        self.delivery_dest_lines = delivery_dest_line_ids
    
        return {
            'res_id': show_id,
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'delivery.dest.location',
            'type': 'ir.actions.act_window',
            'target':'new',
        }
       
    @api.v8
    @api.onchange('pkg_number')
    def change_pkg_number(self):
        ''''''
        self.info = ''
        self.receive_lines = []
        self.state = 'draft'
        if self.pkg_number:
            bill_line_obj = self.env['delivery.bill.line']
            parent_pkg_objs = bill_line_obj.search(['|',('parent_pkg_number','=',self.pkg_number),('pkg_number','=',self.pkg_number)])
            if parent_pkg_objs:
                wait_for_receive = 0
                for line in parent_pkg_objs:
                    if line.state != 'waiting':
                        wait_for_receive = 1
                    else:
                        wait_for_receive = 2
                if 1 == wait_for_receive:
                    self.info = u"系统中包号：'%s'的状态不为等待收货" % self.pkg_number  
                   
            if not parent_pkg_objs and self.pkg_number:
                self.info = u"系统中的送货当中没有包号:\"%s\"的信息或者对应的包状态不为等待收货" % self.pkg_number  
                self.receive_lines = []
                self.state = 'draft'
            receive_lines = []
            for line in parent_pkg_objs:
                if line.state != 'waiting':
                    continue
                values ={
                    'purchase_number':line.purchase_number,
                    'delivery_bill_line_id':line.id,
                    'parent_pkg_number':line.parent_pkg_number,
                    'pkg_number':line.pkg_number,
                    'supplier_code':line.supplier_code,
                    'product_id':line.product_id,
                    'product_qty':line.product_qty,
                    'net_weight':line.net_weight,
                    'gross_weight':line.gross_weight,
                    'actual_product_qty':line.product_qty,
                    'actual_net_weight':line.net_weight,
                    'actual_gross_weight':line.gross_weight,
                }
                receive_lines.append((0,0,values))
            if receive_lines:
                self.receive_lines = receive_lines
                self.state = 'info'
            
            

class delivery_dest_location(models.TransientModel):
    _name = 'delivery.dest.location' 
    name = fields.Char(string='name')
    line_ids = fields.One2many('delivery.dest.location.line','bill_line',string='delivery receive line')
    
    @api.multi
    def continue_receive(self):
        '''继续收货'''
        self.ensure_one()
        return {
            'view_type': 'form',
            "view_mode": 'form',
            'view_id': self.env.ref('batar_delivery_receive.delivery_receive_form').id,
            'res_model': 'delivery.receive',
            'type': 'ir.actions.act_window',
            'target':'_blank',
        } 
  
          
class delivery_dest_location_line(models.TransientModel):
    _name = 'delivery.dest.location.line'
    bill_line  = fields.Many2one('delivery.dest.location',string='delivery receive line')
    location_id = fields.Many2one('stock.location', string='stock location')   
    product_id = fields.Many2one('product.product',string='product')
    default_code = fields.Char(related='product_id.default_code',string='default code')
    product_qty =fields.Float(string='product quantity')
    net_weight= fields.Float(string='net weight')
      
    
class delivery_receive_line(models.TransientModel):
    _name = "delivery.receive.line"
    bill_line  = fields.Many2one('delivery.receive',string='delivery receive') 
    delivery_bill_line_id = fields.Many2one('delivery.bill.line',string='delivery bill line')
    purchase_number = fields.Char(string='purchase order')
    parent_pkg_number = fields.Char(string='parent package number')
    pkg_number= fields.Char(string='package number')
    supplier_code = fields.Char(string='supplier code')
    product_id = fields.Many2one('product.product',string='product')
    default_code = fields.Char(string='default code')
    product_qty =fields.Float(string='product quantity')
    net_weight= fields.Float(string='net weight')
    gross_weight = fields.Float(string='gross weight')
    
    
    actual_product_qty =fields.Float(string='actual product quantity')
    actual_net_weight= fields.Float(string='actual net weight')
    actual_gross_weight = fields.Float(string='actual gross weight')
    name= fields.Char(compute="_name_get",string='name')
    
    @api.one
    @api.depends("parent_pkg_number","pkg_number")
    def _name_get(self):
        if self.pkg_number and self.parent_pkg_number :
            self.name = "%s:%s" %(self.parent_pkg_number,self.pkg_number)
        elif self.pkg_number:
            self.name = self.pkg_number
        else:
            self.name = ''
    
    