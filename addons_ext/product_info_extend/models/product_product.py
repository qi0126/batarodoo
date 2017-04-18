# -*- coding: utf-8 -*-
'''
Created on 2016年2月25日

@author: cloudy
'''
from openerp import fields,models,api,_
from openerp.exceptions import UserError
import re
  



class prdouct_product(models.Model):
    _inherit = "product.product"
    
    @api.multi
    def _get_product_material(self):
        '''获得产品材质'''
        for line in self:
            for attribute_value_id in line.attribute_value_ids:

                if attribute_value_id.attribute_id.code == 'material':
                    line.material= attribute_value_id.name

                  
    standard_weight = fields.Float(compute='_compute_attribute',string="Standard Weight")
    item_fee = fields.Float(string="Item Fee")
    weight_fee = fields.Float(string="weight fee")
    additional_fee = fields.Float(string='additional fee') 
    ponderable = fields.Boolean(related='product_tmpl_id.ponderable',store=True,string='ponderable')
    real_time_price_unit = fields.Float(compute='_compute_attribute',string='real time price unit')
    sale_price = fields.Char(compute='_compute_sale_price',string='display sale price')
    default_code = fields.Char(compute='_compute_default_code',store=True,string='default code')
    material = fields.Char(compute='_get_product_material',string='material')
    barcode_image = fields.Binary(string='barcode image')
    supplier_lines = fields.One2many('product.supplierinfo','product_id',string='product supplier')
    string_attribute = fields.Char(string=u'所有属性',store=True,compute="_compute_default_code")
     
    
    
    @api.one
    @api.depends("attribute_value_ids")
    def _compute_default_code(self):
        '''生成编码'''
       

        attribute_value_ids = self.attribute_value_ids
        firstCode =None
        SecondCode = {}
        thirdCode=''
        default_code=''
        attribute_strings = ''
        first_str =''
        secondStr = []
        end_str = ''
        extendCode = {}
        extendCodeStr = ''
        for attribute_value_id in attribute_value_ids:
            if not attribute_value_id.attribute_id.part_code:
                extendCode[attribute_value_id.attribute_id.name] = "%s" % attribute_value_id.sequence
            elif attribute_value_id.attribute_id.code == 'material':
                firstCode = attribute_value_id.sequence
                first_str = "%s:%s" % (attribute_value_id.attribute_id.name,attribute_value_id.name)
            elif attribute_value_id.attribute_id.code == 'weight':
                end_str = "%s:%s" % (attribute_value_id.attribute_id.name,attribute_value_id.name)
                m = re.match(r"(^[0-9]\d*\.\d|\d+)",attribute_value_id.name)
                thirdCode =  m.group(1)
            else:
                SecondCode[attribute_value_id.attribute_id.name] = "%s" % attribute_value_id.sequence
                s="%s:%s" % (attribute_value_id.attribute_id.name,attribute_value_id.name)
                secondStr.append(s)    
            if firstCode:
                default_code = "%s0%s" % (firstCode,self.product_tmpl_id.sequence)
            else:
                default_code = "%s" % (self.product_tmpl_id.sequence)
            if SecondCode:
                 
                SecondCodeStr = "0".join([SecondCode[v] for v in sorted(SecondCode.keys())])
                default_code = "%s0%s"%(default_code,SecondCodeStr)
            if extendCode:
                extendCodeStr = "0".join([extendCode[v] for v in sorted(extendCode.keys())])
            if extendCodeStr:
                default_code = "%s-%s"%(default_code,extendCodeStr)
            if thirdCode:
                default_code = "%s/%s"%(default_code,thirdCode)
            attribute_strings = ";".join(secondStr)
            attribute_strings = "%s;%s" %(first_str,attribute_strings)
            
            if end_str:
                attribute_strings = "%s;%s" %(attribute_strings,end_str)
        self.default_code = default_code
        self.string_attribute = attribute_strings
        
            
    

    _defaults = {
        'type': "product",
        'ponderable':True,
    }
    _sql_constraints = [
        ('default_uniq', 'unique(default_code)', u'内部货号必须唯一!'),
    ]

    
    @api.multi
    def _compute_sale_price(self):
        '''根据不同类型的产品显示显示销售价格'''
      
        for line in self:
            if line.ponderable:
                line.sale_price = "%s/g" % line.real_time_price_unit
            else:
                line.sale_price = "%s/件" % line.list_price
     
    @api.multi
    def _compute_attribute(self):
        '''获得某个类别的实时单价'''
        #默认为0
        for product in self:
            product.standard_weight = 0
            product.real_time_price_unit = 0
            #为可称量产品
            if product.ponderable:
                attribute_value_ids = product.attribute_value_ids
                for line in attribute_value_ids:
                    if line.attribute_id.code == "material":
                        materail_price = self.env['product.attribute.material.price'].\
                        search([('attribute_value_id','=',line.id),('attribute_id','=',line.attribute_id.id),('active','=',True)])
                        product.real_time_price_unit = materail_price.price_unit
                    if line.attribute_id.code == "weight":       
                        m= re.match(r"(^[0-9]\d*\.\d|\d+)", line.name) 
                        weight = m.group(1)
                        product.standard_weight = float(weight)           
#     def _gen_default_code(self,attribute_value_ids,product_tmpl_id):
#         '''生成编码'''
#         tmplObj = self.env['product.template'].search([('id','=',product_tmpl_id)])
#          #下面3个list用于生成编码
#         firstCode =None
#         SecondCode = {}
#         thirdCode=''
#         default_code=''
#         
#         if attribute_value_ids:
#             material=self.env['ir.model.data'].get_object_reference('product_info_extend', 'product_attribute_material')[1]
#             attribute_value_ids = attribute_value_ids[0]
#             if len(attribute_value_ids) ==2:
#                 attribute_value_ids = attribute_value_ids
#             elif len(attribute_value_ids) ==3:
#                 attribute_value_ids = attribute_value_ids[2]
#             print "attribute_value_ids:",attribute_value_ids
#             value_objs = self.env['product.attribute.value'].search([('id','in',attribute_value_ids)])
#             for line in value_objs:
#                 if line.attribute_id.code == 'material':
#                     firstCode = line.sequence
#                 elif line.attribute_id.code == 'weight':
#                     m = re.match(r"(^[0-9]\d*\.\d|\d+)",line.name)
#                     thirdCode =  m.group(1)
#                 else:
#                     SecondCode[line.attribute_id.name] = "%s" % line.sequence
#                      
#             if firstCode is None:
#                 raise UserError(_("Must set the material of the product")) 
#             default_code = "%s0%s" % (firstCode,tmplObj.sequence)
#             if SecondCode:
#                  
#                 SecondCodeStr = "0".join([SecondCode[v] for v in sorted(SecondCode.keys())])
#                 default_code = "%s-%s"%(default_code,SecondCodeStr)
#             if thirdCode:
#                 default_code = "%s-%s"%(default_code,thirdCode)
#              
#         else:
#             raise UserError(_("Must set the properties of the product")) 
#          
#         return default_code
        




            