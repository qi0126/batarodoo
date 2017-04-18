# -*- coding: utf-8 -*-
'''
Created on 2016年5月17日

@author: cloudy
'''

from openerp import fields,models,api, _
from openerp.exceptions import UserError
from openerp.tools.common_ext import ImportExcelFile


class product_attribute_value_import(models.TransientModel):
    _name ="product.attribute.value.import"
    
    file = fields.Binary("Excel File")
    attribute_id = fields.Many2one('product.attribute',stirng='product attribute')
    _Titles ={
        "name":u"属性值",
    }
    
    def checkExsit(self,attribute_id=None,attribute_value_list=[]):
        '''检查是否重复'''
        result = []
        exsit_name = []
        if attribute_id is None:
            raise UserError(_(u"请先选择属性"))
        if not attribute_value_list:
            raise UserError(_(u"不能获得属性值，请联系系统管理员"))
        attributeObj = self.env['product.attribute.value']
        for one in attribute_value_list:
            line = one
            if attribute_id.code == 'weight':
                line = "%sg"%one

            obj = attributeObj.search([('attribute_id','=',attribute_id.id),("name",'=',line)])
            print obj
            if obj:
                result.append(obj.id)
                exsit_name.append(one)
            
        return result,exsit_name
            
    @api.multi
    def apply(self):
        ''''''
        ids = []
        excel_obj = ImportExcelFile(self.file)
        data = excel_obj.readFile()
        if not data:
            raise UserError(u"属性值为空")
        
        check_data = data.get('data',[])
        if not check_data:
            raise UserError(u"数据内容不符合要求，请联系管理员确认模版")
        test_line = check_data[0]
        if test_line.get(self._Titles['name'],'')=='':
            raise UserError(_(u"请确认导入数据列中有'属性值'"))
        all_attribute_value_list = [line.get(self._Titles['name'],'') for line in check_data if line]
        attribute_value_list = []
        #检查属性值是否有重复
        for line in all_attribute_value_list:
            if line not in attribute_value_list:
                attribute_value_list.append(line)
        #检查属性值在系统中是否已经存在
        check_result,exsit_name = self.checkExsit(self.attribute_id, attribute_value_list)
        ids += check_result
        attributeObj = self.env['product.attribute.value']
        for line in attribute_value_list:
            if line in exsit_name:
                continue
            if not line:
                continue
            id = attributeObj.create({"name":line,"attribute_id":self.attribute_id.id})
            if id:
                ids.append(id.id)
        return {
            'name': _(u'属性值导入结果'),
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'product.attribute.value',
            "domain": [('id', 'in', ids)],
            'type': 'ir.actions.act_window',
        }
        
        