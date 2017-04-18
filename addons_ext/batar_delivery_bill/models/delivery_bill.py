# -*- coding: utf-8 -*-
'''
Created on 2016年5月2日

@author: cloudy
'''
from openerp import models,fields,api,_

class delivery_bill(models.Model):
    _name = 'delivery.bill'
    _order = 'id desc,write_date desc'
      
    _STATE = [
        ('draft','draft'),
        ('confirm', 'confirm'),
        ('check','generate check order')

    ]
    name = fields.Char(string='delivery bill name')
    charge_man = fields.Many2one('res.users',string='ERP charge man')
    
    partner_id = fields.Many2one('res.partner',store=True,string='partner')
    partner_person = fields.Char(string='supplier charge man')
    partner_mobile = fields.Char(string='supplier charge man mobile')
    delivery_method = fields.Char(string='delivery method')
    delivery_man = fields.Char(string='delivery charge man')
    delivery_mobile = fields.Char(string='delivery charge man mobile')
    state = fields.Selection(_STATE,string='state',default='draft')
    line_id = fields.One2many('delivery.bill.line','delivery_id',string='delivery bill line')
#     picking_id = fields.Many2one('stock.picking',string='stock picking')
    location_src_id = fields.Many2one('stock.location',string='source location')
    location_dest_id = fields.Many2one('stock.location',string='dest location')
    
    total_qty = fields.Float(string='total quantity',compute="get_total_info",default=0)
    total_net_weight = fields.Float(string='total net weight',compute="get_total_info",default=0)
    total_gross_weight = fields.Float(string='total gross weight',compute="get_total_info",default=0)

    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('delivery bill name must be unique!')), 
    ]



    @api.one
    @api.depends('line_id','state')
    def get_total_info(self):
        '''获得统计信息'''
        total_qty = 0
        total_net_weight = 0
        total_gross_weight = 0

        for line in self.line_id:
            total_qty += line.product_qty
            total_net_weight += line.net_weight
            total_gross_weight += line.gross_weight
        self.total_qty = total_qty
        self.total_net_weight = total_net_weight
        self.total_gross_weight = total_gross_weight

        
    @api.multi
    def confirm(self):
        '''确认送货单'''
        self.write({'state':'confirm'})
        bill_line = self.env['delivery.bill.line'].search([('delivery_id','in',self.ids),('state','=','draft')])
        if bill_line:
            bill_line.write({'state':'confirm'})






        
        
class delivery_bill_line(models.Model):
    _name = 'delivery.bill.line'
    _order = 'id desc,write_date desc'
    _STATE = [
        ('draft', 'draft'),
        ('confirm', 'confirm'),
        ('check', 'generate check order')

    ]
    name= fields.Char(compute="_name_get",string='name')
    partner_id = fields.Many2one(related='delivery_id.partner_id',string='partner')
    delivery_id = fields.Many2one('delivery.bill',ondelete='cascade',string='delivery bill')
    purchase_number = fields.Char(string='purchase order')
    packing_code = fields.Char(string='packing code')
    parent_pkg_number = fields.Char(string='parent package number')
    pkg_number = fields.Char(string='package number')
    supplier_code = fields.Char(string='supplier code')
    default_code = fields.Char(string='default code')
    product_id = fields.Many2one('product.product',string='product')
    product_qty = fields.Float(string='product quantity')
    net_weight = fields.Float(string='net weight')
    gross_weight = fields.Float(string='gross weight')
    note = fields.Text(string='note')
    state = fields.Selection(_STATE,string='state')
    must_check = fields.Boolean(default=False,string='must check')



    _sql_constraints = [
        ('pkg_number_uniq', 'unique(pkg_number)', _('package number  must be unique!')), 
    ]
    _defaults={
        'state':'draft',
    }
    @api.depends('state')
    def compute_delivery_line_info(self):
        for line in self:
            line.delivery_id.get_total_info()
    @api.one
    @api.depends("parent_pkg_number","pkg_number")
    def _name_get(self):
        if self.pkg_number and self.parent_pkg_number :
            self.name = "%s:%s" %(self.parent_pkg_number,self.pkg_number)
        elif self.pkg_number:
            self.name = self.pkg_number
        else:
            self.name = ''
            

        
            
        
    