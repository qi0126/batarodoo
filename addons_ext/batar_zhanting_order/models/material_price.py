#!/usr/bin/env python
#coding=utf8
'''
Created on 2016/8/23

@author: cloudy
'''

from openerp import fields,models




class zhanting_material_price(models.Model):
    _name ='zhanting.material.price'

    order_id = fields.Many2one('batar.customer.sale',ondelete='cascade',string='customer sale order')
    attribute_value_id = fields.Many2one('product.attribute.value',string='product attribute value')
    attribute_id = fields.Many2one('product.attribute',\
                                   default= lambda self:self.env['ir.model.data'].get_object_reference('product_info_extend', 'product_attribute_material')[1],string='product attribute')
    price_discount = fields.Float(string='price discount')
    price_unit = fields.Float(string='real time material price')
    _sql_constraints = [
        ('unique', 'unique(order_id, attribute_value_id)','one order attribute value must unique!'),
    ]