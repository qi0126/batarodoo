# -*- coding: utf-8 -*-
'''
Created on 2016年4月19日

@author: cloudy
'''
from openerp import models,fields,api,_
from openerp.exceptions import UserError
    
class product_discount(models.Model):
    _name ='product.discount'
    Applied_On = [('3_global', 'global'),
                  ('2_product_category', 'product category'), 
                  ('1_product', 'product'), 
                  ('0_product_variant', 'product variant')]
    applied_on = fields.Selection(Applied_On,string='applied on')
    name = fields.Char(string='name')
    partner_id = fields.Many2one('res.partner',string='customer')
    categ_id = fields.Many2one('product.category',string='product category')
    product_tmpl_id = fields.Many2one('product.template',string='product template',ondelete='cascade')
    product_id = fields.Many2one('product.product',string='product')
    date_start = fields.Date(string='start date')
    date_end = fields.Date(string='end date')
    min_quantity = fields.Float(string='min quantity',default=1.0)
    
    item_fee = fields.Float(related='product_id.item_fee', string='item fee')
    weight_fee =fields.Float(related='product_id.weight_fee', string='weight fee')
    additional_fee = fields.Float(string='additional fee') 
    
    item_fee_discount = fields.Float(string='item fee discount')
    weight_fee_discount =fields.Float(string='weight fee discount')
    additional_fee_discount = fields.Float(string='additional fee discount') 
    
    item_fee_discount_percent = fields.Integer(string='item fee discount percent')
    weight_fee_discount_percent =fields.Integer(string='weight fee discount percent')
    additional_fee_discount_percent = fields.Float(string='additional fee discount percent') 
    
    is_percent = fields.Boolean(string='discount depend on percent')
    active = fields.Boolean(string='active')
    attribute_value_id = fields.Many2one('product.attribute.value',string='product attribute value')
    attribute_id = fields.Many2one('product.attribute',\
                                   default= lambda self:self.env['ir.model.data'].get_object_reference('product_info_extend', 'product_attribute_material')[1],string='product attribute')
    ponderable = fields.Boolean(related='product_id.ponderable',string='ponderable')
    discount_amount = fields.Float(string='discount amount')
    discount_percent = fields.Integer(string='discount percent')
    
    _sql_constraints = [
        ('uniq', 'unique(partner_id,categ_id,product_tmpl_id,product_id,active)', 'must be unique!'), 
    ]
    
    @api.onchange('product_id','item_fee_discount_percent','weight_fee_discount_percent','additional_fee_discount_percent')
    def product_id_change(self):
        ''''''
        if self.product_id:
            self.item_fee = self.product_id.item_fee
            self.weight_fee = self.product_id.weight_fee
            self.additional_fee = self.product_id.additional_fee
        if self.weight_fee_discount_percent:
            if self.weight_fee_discount_percent >= 100 or  self.weight_fee_discount_percent < 0:
                raise  UserError(u'基础工费优惠的范围为大于等于0，小于100')
        if self.item_fee_discount_percent:
            if self.item_fee_discount_percent >= 100 or  self.item_fee_discount_percent < 0:
                raise  UserError(u'件工费优惠的范围为大于等于0，小于100')
        if self.additional_fee_discount_percent:
            if self.additional_fee_discount_percent >= 100 or  self.additional_fee_discount_percent < 0:
                raise  UserError(u'附加工费优惠的范围为大于等于0，小于100')
    
    @api.multi
    def cancel_discount(self):
        '''取消优惠'''
        self.write({'active':False})
    
    @api.model
    def create(self, vals):
        name =  _('no select')
        partner_id = vals.get('partner_id',None)
        
        applied_on = vals.get('applied_on','')
        if '3_global' == applied_on:
            name =  _('all products')
            obj = self.search([('partner_id','=',partner_id),('applied_on','=','3_global')])
            if obj:
                obj.write({'active':False})
        elif '2_product_category' == applied_on:
            categ_id = vals.get('categ_id',None)
            if categ_id:
                name  = self.env['product.category'].search([('id','=',categ_id)]).name
                obj = self.search([('partner_id','=',partner_id),('categ_id','=',categ_id)])
                if obj:
                    obj.write({'active':False})
        elif '1_product' == applied_on:
            product_tmpl_id = vals.get('product_tmpl_id',None)
            if product_tmpl_id:
                name = self.env['product.template'].search([('id','=',product_tmpl_id)]).name
                obj = self.search([('partner_id','=',partner_id),('product_tmpl_id','=',product_tmpl_id)])
                if obj:
                    obj.write({'active':False})
        elif '0_product_variant' == applied_on:
            product_id = vals.get('product_id',None)
            if product_id:
                name = self.env['product.product'].search([('id','=',product_id)]).name
                obj = self.search([('partner_id','=',partner_id),('product_id','=',product_id)])
                if obj:
                    obj.write({'active':False})
                   
        vals['active'] = True
        vals['name'] =  name 
        return super(product_discount,self).create(vals)
    
    
    
    