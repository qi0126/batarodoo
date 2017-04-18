# -*- coding: utf-8 -*-
'''
Created on 2016年4月22日

@author: cloudy
'''
from openerp import fields,models,api,_
from openerp.exceptions import UserError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import time
import re


class sale_order_line(models.Model):
    _inherit = "sale.order.line"
    
    @api.one
    @api.depends('product_id')
    def _real_time_price_unit(self):
        ''''''
        if self.product_id:
            material_value_id,price_dict = self._get_material_value_id()
            if material_value_id and price_dict:
                self.real_time_price_unit = price_dict[material_value_id]
        else:
            self.real_time_price_unit = self.product_id.real_time_price_unit
               
    real_time_price_unit = fields.Float(compute='_real_time_price_unit',string='real time price unit')
    standard_weight = fields.Float(string="Standard Weight")
    all_weights = fields.Float(string='all line weight')
    item_fee = fields.Float(string="Item Fee",compute="_product_fee",store=True)
    additional_fee = fields.Float(string='additional fee',compute="_product_fee",store=True)
    weight_fee = fields.Float(string="weight fee",compute="_product_fee",store=True)

    
    _sql_constraints = [
        ('order_line_product', 'unique(product_id, order_id)', 'product must be unique per order!'),
    ]
      
    defaults = {
        'picking_policy':'one',
        'all_weights':0,
    }
    
    @api.model
    def create(self, vals):
        order_id =  vals.get('order_id',None)
        if order_id:
            order = self.env['sale.order'].search([('id','=',order_id)])
            if order:
                vals['tax_id']= order.order_tax_id
        
        return super(sale_order_line,self).create(vals)
    
    @api.v8
    @api.onchange('product_id','product_uom_qty','standard_weight')
    def all_weights_compute(self):
        ''''''
        self.product_uom_qty = int(self.product_uom_qty)
        self.all_weights= self.product_uom_qty*self.standard_weight
        self.order_id.get_total_info()
       
#     @api.one
#     @api.depends('standard_weight')
#     def sale_order_compute(self):
#         ''''''
#         self.order_id.get_total_info()
            
    def _time_vaild(self,time_stamp=int(time.time()),product_discount_obj=None):
        '''判断时间是否有效'''
        if product_discount_obj is None:
            return False
        flag = True
        date_start = product_discount_obj.date_start
        date_end = product_discount_obj.date_end
        #判断时间是否有效，若优惠没有设置时间期限，则一直有效
        if date_start:
            date_start_time_stamp = int(time.mktime(time.strptime(date_start,DATE_FORMAT)))
            #当前时间在优惠开始日期之前
            if time_stamp < date_start_time_stamp:
                flag = False
        if date_end:
            date_end_time_stamp = int(time.mktime(time.strptime(date_end,DATE_FORMAT)))
            #当前时间在优惠结束日期之后
            if time_stamp > date_end_time_stamp:
                flag = False
        return flag
    
    def _get_fee(self,product_discount=None):
        ''''''
        if (int(self.product_uom_qty) >= int(product_discount.min_quantity)):
            #如果产品是可称量的产品
            if self.product_id.ponderable:
                #根据优惠百分比设置工费信息
                if product_discount.is_percent:
                    self.additional_fee = (100-product_discount.additional_fee_discount_percent)*self.product_id.additional_fee
                    self.weight_fee = (100-product_discount.weight_fee_discount_percent)*self.product_id.weight_fee
                    self.item_fee = (100-product_discount.item_fee_discount_percent)*self.product_id.item_fee
                #根据优惠金额设置工费信息
                else:
                    self.additional_fee = self.product_id.additional_fee - product_discount.additional_fee_discount
                    self.weight_fee = self.product_id.weight_fee - product_discount.weight_fee_discount
                    self.item_fee = self.product_id.item_fee - product_discount.item_fee_discount
            #产品为不可称量的产品，即按件卖
            else:
                #根据百分比设置
                if product_discount.is_percent:
                    pass
                #根据金额设置
                else:
                    pass
                
    
    def _get_material_value_id(self):
        '''返回产品的材质'''
        #获得价格，工费等信息，
        material_price_lines = self.order_id.material_price_line
        material_price_dict = {}
        material_value_id = None
        for line in material_price_lines:
            material_price_dict[line.attribute_value_id.id] = line.price_unit    
        attribute_value_ids =  self.product_id.attribute_value_ids
        value_ids = material_price_dict.keys()
        for attribute_value_id in attribute_value_ids:
            value_id = attribute_value_id.id 
            if value_id in value_ids:
                material_value_id = value_id
        return [material_value_id,material_price_dict]
    
    @api.one
    @api.depends('product_id','order_id.partner_id')
    def _product_fee(self):
        if self.product_id:
            if not self.order_id.partner_id:
                raise UserError(_(u'选择产品前需要选择客户'))
            
            material_value_id = self._get_material_value_id()[0]
            #当前时间，用于判断订单明细创建时间是否符合优惠时效
            now_date_time_stamp = int(time.time())
            #获得工费信息
            #如果对客户的具体产品进行设置
            #搜索条件：优惠有效，具体的产品
            product_discount_first = self.env['product.discount'].search([('partner_id','=',self.order_id.partner_id.id),('product_id','=',self.product_id.id),('active','=',True)])
            product_discount_second = self.env['product.discount'].search([('partner_id','=',self.order_id.partner_id.id),('attribute_value_id','=',material_value_id),('product_tmpl_id','=',self.product_id.product_tmpl_id.id),('active','=',True)])
            product_discount_third = self.env['product.discount'].search([('partner_id','=',self.order_id.partner_id.id),('categ_id','=',self.product_id.categ_id.id),('active','=',True)])
            product_discount_fourth = self.env['product.discount'].search([('partner_id','=',self.order_id.partner_id.id),('applied_on','=','3_global'),('active','=',True)])
            
            #如果有标准重量，写入标准重量
            attribute_value_ids =  self.product_id.attribute_value_ids
            
            for attribute_value_id in attribute_value_ids:
                if attribute_value_id.attribute_id.code == "weight":
                    m = re.match(r"(^[0-9]\d*\.\d|\d+)",attribute_value_id.name)
                    if m:
                        standard_weight = m.group(1)
                        self.standard_weight = float(standard_weight)
            
            #如果有产品系列优惠
            if product_discount_first:
                if self._time_vaild(now_date_time_stamp, product_discount_first):
                    #优惠在时效内,并且最小购买数量符合要求
                    self._get_fee(product_discount_first)
            #如果存在产品模版优惠
            elif product_discount_second:
                if self._time_vaild(now_date_time_stamp, product_discount_second):
                    #优惠在时效内,并且最小购买数量符合要求
                    self._get_fee(product_discount_second)
            #如果存在产品类别优惠
            elif product_discount_third:
                if self._time_vaild(now_date_time_stamp, product_discount_third):
                    #优惠在时效内,并且最小购买数量符合要求
                    self._get_fee(product_discount_third)
            #如果存在所有产品优惠
            elif product_discount_fourth:
                if self._time_vaild(now_date_time_stamp, product_discount_fourth):
                    #优惠在时效内,并且最小购买数量符合要求
                    self._get_fee(product_discount_fourth)
            #如果优惠不存在，使用产品默认的费用
            else:
                self.additional_fee = self.product_id.additional_fee
                self.weight_fee = self.product_id.weight_fee
                self.item_fee = self.product_id.item_fee
            
        
    
    @api.onchange('product_uom_qty', 'tax_id','all_weights','standard_weight')            
    @api.depends('product_uom_qty', 'tax_id','all_weights','standard_weight')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
      
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)  
            weight_fee = line.additional_fee+line.weight_fee
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,\
                                             product=line.product_id, partner=line.order_id.partner_id,ponderable=line.product_id.ponderable,
                                             real_time_price_unit=line.real_time_price_unit,item_fee=line.item_fee,\
                                             weight_fee=weight_fee, standard_weight=line.standard_weight,all_weights=line.all_weights)
            
            values = {
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            }
            line.update(values)
            