# -*- coding: utf-8 -*-
'''
Created on 2016年3月18日

@author: cloudy
'''
from openerp import models,fields,api,_
from openerp.exceptions import UserError


class product_attribute_material_price(models.Model):
    _name = 'product.attribute.material.price'
    
    @api.one
    @api.onchange('ornament_price', 'material_price')
    def _get_price_total(self):
        ''''''
        self.price_unit = self.material_price + self.ornament_price
        
    attribute_id = fields.Many2one('product.attribute',default= lambda self:self.env['ir.model.data'].get_object_reference('product_info_extend', 'product_attribute_material')[1])
    attribute_value_id = fields.Many2one('product.attribute.value',string='product attribute value')
    active = fields.Boolean(string='active')
    material_price = fields.Float(string='material price')
    ornament_price = fields.Float(string="ornament price")
    price_unit = fields.Float(compute='_get_price_total',string='price unit total')
    
    _sql_constraints = [
        ('material_price', 'CHECK(material_price > 0.0)',_('material price must be greater than 0.0!')),
        
    ]

    _defaults = {
        'active':True,
    }
    
    @api.multi
    @api.depends('attribute_id','attribute_value_id')
    def name_get(self):
        result = []
        for line in self:
            name = "%s:%s" % (line.attribute_id.name,line.attribute_value_id.name)
            result.append((line.id,name))
        return result
    
    @api.model
    def create(self, vals):
        '''保存前使之前的价格无效'''
        
        material_price = vals.get('material_price',-1)
        ornament_price = vals.get('ornament_price',-1)
        if (material_price < 0) or (ornament_price < 0) :
            raise UserError(_(u'材质价格和饰品价格必须大于0'))
        attribute_value_id = vals.get('attribute_value_id',None)  
        
        if not attribute_value_id:
            raise UserError(u'属性值无效')
        records = self.env['product.attribute.material.price'].search([('active','=',True),('attribute_value_id','=',attribute_value_id)])
        if records:
            records.write({'active':False})
        return super(product_attribute_material_price,self).create( vals)