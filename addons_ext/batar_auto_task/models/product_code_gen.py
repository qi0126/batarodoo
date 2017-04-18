# -*- coding: utf-8 -*-
'''
Created on 2016年7月4日

@author: cloudy
'''
from openerp import models,api
import re

class product_code_gen(models.TransientModel):
    _name = 'product.code.gen'
    
    @api.model
    def auto_product_code_gen(self):
        ''''''
        product_list = self.env['product.product'].search([])
        for product_line in product_list:
            attribute_value_ids = product_line.attribute_value_ids
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
                    default_code = "%s0%s" % (firstCode,product_line.product_tmpl_id.sequence)
                else:
                    default_code = "%s" % (product_line.product_tmpl_id.sequence)
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

                product_line.default_code = default_code
                product_line.string_attribute = attribute_strings
         