# -*- coding: utf-8 -*-
'''
Created on 2016年2月24日

@author: cloudy
'''

from openerp import fields,models,api,_
from openerp.exceptions import UserError


 
class sale_order(models.Model):
    _inherit = 'sale.order'
      
    material_price_line = fields.One2many('sale.order.material.price','order_id',string='sale order material price')
    order_tax_id = fields.Many2many('account.tax',string='account tax')
    total_qty = fields.Float(string='total quantity',compute="get_total_info")
    total_weight = fields.Float(string='total weight',compute="get_total_info")
    order_type = fields.Selection([('pad','pad'),('pc','pc'),('batch','batch')],string='order type',default='pc')

    #用于删除订单后释放库存
    @api.multi
    def unlink(self):
        """删除订单"""
        product_ids = []
        for line in self:
            for order_line in line.order_line:
                product_ids.append(order_line.product_id.id)
        result = super(sale_order, self).unlink()
        products = self.env['product.product'].search([('id','in',product_ids)])
        for product in products:
            if product.qty_available:
                pass
        return  result

    # 用于删除订单后释放库存
    @api.multi
    def action_cancel(self):
        """"""
        self.write({'state': 'cancel'})
        for line in self:
            for order_line in line.order_line:
                if order_line.product_id.qty_available >0:
                    pass
    @api.one
    @api.depends('order_line')
    def get_total_info(self):
        ''''''
        total_qty = 0
        total_weight = 0
        for line in self.order_line:
            total_qty += line.product_uom_qty
            total_weight += line.all_weights
        self.total_qty = total_qty
        self.total_weight = total_weight
    
           
    @api.onchange('order_tax_id')
    def change_order_tax_id(self):
        '''订单税率改变，明细行的税率也将改变'''
        for line in self.order_line:
            line.tax_id = self.order_tax_id
     
    @api.onchange('partner_id')
    def partner_change(self):
        '''根据客户获得客户的基础价格信息'''
        
        material_price_line = []
        if self.partner_id:
            price_discount = 0
            attribute_id = self.env['ir.model.data'].get_object_reference('product_info_extend', 'product_attribute_material')[1]
            attribute_values = self.env['product.attribute.value'].search([('attribute_id','=',attribute_id)])
            for attribute_value in attribute_values:
                #搜索是否针对客户设置了材质价格
                customer_ornament_price_obj=self.env['customer.ornament.price'].search([('partner_id','=',self.partner_id.id),('attribute_value_id','=',attribute_value.id),('active','=',True)])
                price_unit = 0
                #若存在为客户单独设置的材质价格
                if customer_ornament_price_obj:
                    price_unit = customer_ornament_price_obj.price_unit
                    price_discount = customer_ornament_price_obj.price_discount
                #若没有设置材质价格，采用系统当前的材质价格作为默认的价格
                else:
                    price_unit = self.env['product.attribute.material.price'].search([('active','=',True),('attribute_value_id','=',attribute_value.id)]).price_unit
                values = {
                   
                    'attribute_value_id':attribute_value.id,
                    'price_unit':price_unit,
                    'price_discount':price_discount
                }
                material_price_line.append((0,0,values))
            self.material_price_line = material_price_line
    
  
            
            
class sale_order_material_price(models.Model):
    _name ='sale.order.material.price'

    order_id = fields.Many2one('sale.order',ondelete='cascade',string='sale order')
    attribute_value_id = fields.Many2one('product.attribute.value',string='product attribute value')
    attribute_id = fields.Many2one('product.attribute',\
                                   default= lambda self:self.env['ir.model.data'].get_object_reference('product_info_extend', 'product_attribute_material')[1],string='product attribute')
    price_discount = fields.Float(string='price discount')
    price_unit = fields.Float(string='real time material price')
    _sql_constraints = [
        ('unique', 'unique(order_id, attribute_value_id)','one order attribute value must unique!'),
    ]

