# -*- coding: utf-8 -*-
'''
Created on 2016年3月18日

@author: cloudy
'''
from openerp import models,fields,api,_
from openerp.exceptions import UserError
from openerp.tools.common_ext import GetNextSequence
import re


class product_attribute_line(models.Model):
    _inherit ='product.attribute.line'
    _sql_constraints = [
        ('attribute_uniq', 'unique(attribute_id, product_tmpl_id)',u"属性必须唯一"),
    ]
        
class product_attribute(models.Model):
    _inherit = 'product.attribute'
    code = fields.Char(string='product attribute code')
    part_code = fields.Boolean(default=True,string='Participate in coding')
    name= fields.Char('Name', translate=False, select=True)
    _sql_constraints = [
        ('code_uniq', 'unique(code)',u"属性编码必须唯一"), 
        ('name_uniq', 'unique(name)', u"属性名称必须唯一"), 
    ]
    @api.multi
    def write(self, vals):
        code = vals.get('code','')
        if code:
            vals['code']= code.strip()
        return super(product_attribute,self).write(vals)
    @api.model
    def create(self, vals):
        code = vals.get('code','')
        attributeObj  = self.env['product.attribute'].search([],limit=1,order='id desc')
        sequence = 1
        if attributeObj:
            sequence = GetNextSequence.GetNextSequence(attributeObj.sequence)
        vals['sequence'] = sequence
        if code:
            vals['code'] = code.strip()
        return super(product_attribute,self).create(vals)

class product_attribute_value(models.Model):
    _inherit = 'product.attribute.value'
    _order = 'id desc'

    name = fields.Char(translate=False)
    _sql_constraints = [
    
        ('attrValue_uniq', 'unique(attribute_id, name)', _(u"属性值必须唯一!")), 
    ]
                        
    @api.multi
    def write(self, vals):
        attribute_id = vals.get('attribute_id',None)
        if attribute_id:
            if self.attribute_id.id != attribute_id:
                raise UserError(u"属性值创建后不能修改属性") 
        weight_attribute_id= self.env['ir.model.data'].get_object_reference('product_info_extend', 'product_attribute_weight')[1]
        if self.attribute_id.id == weight_attribute_id:
            name = vals.get('name','')
            if name:
                m = re.match(r"(^[0-9]\d*\.\d|\d+)",name)
                if not m:
                    raise UserError(_(u'重量的属性值只能为:10或者10g')) 
                vals['name']= '%sg' % m.group(1)
        return super(product_attribute_value,self).write(vals)
    
    @api.model
    def create(self, vals):
        attribute_id = vals.get('attribute_id',None)
        if attribute_id:
            oldattributeValueObj = self.env['product.attribute.value'].search([('attribute_id','=',attribute_id)],limit=1,order='id desc')
            attributeValueObj = self.env['product.attribute.value'].search([],limit=1,order='id desc')
            #修改原有的bug，采用两个兼容之前的记录
            sequence = 1
            if attributeValueObj:
                if oldattributeValueObj.sequence > attributeValueObj.sequence:
                    sequence = oldattributeValueObj.sequence
                else:
                    sequence = attributeValueObj.sequence


            if attributeValueObj:
                sequence = GetNextSequence.GetNextSequence(sequence)
            vals['sequence'] = sequence
       
        attr_obj = self.env['product.attribute'].search([('id','=',attribute_id)])
        if attr_obj.code == 'weight':
            name = vals.get('name','')
            name = "%s"% name
            m = re.match(r"(^[0-9]\d*\.\d|\d+)",name)
            if not m:
                raise UserError(_(u'重量的属性值只能为:10或者10g')) 
            vals['name']= '%sg' % m.group(1)
        return super(product_attribute_value,self).create(vals)
