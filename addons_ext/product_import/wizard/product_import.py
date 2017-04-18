# -*- coding: utf-8 -*-
'''
Created on 2015年12月15日
common_ext为公共函数扩展
@author: cloudy
'''

from openerp.osv import fields,osv
from openerp.tools.common_ext import ImportExcelFile
import unicodedata


class product_category_import(osv.osv_memory):
    _name = 'product.category.import'
    _columns ={
        'file':fields.binary('Excel File',filter='*.xls|*.csv'),
        'action':fields.selection([('update','Update or Create'),('create','Create')],string='import data action'),
    }
    _defaults = {
        'action':'create',
    }
    _Titles = {
        'parent':u'上级分类',
        'product_category':u'分类',
        'name':u'产品名称',
        'attribute':u'属性',
        'attribute_value':u'属性值',
        'sale_ok':u'可销售',
        'price':u'价格',
        'default_code':u'内部编码',
    }
    def apply(self,cr,uid,ids,context=None):
        '''将产品数据导入到系统中'''
        product_obj = self.pool.get('product.template')
        wizard = self.browse(cr, uid, ids[0], context)
        action = wizard.action
        excel_obj = ImportExcelFile(wizard.file)
        data = excel_obj.readFile()
        #对输入的数据进行查重
        check_data = data['data']
        err_check_default_code = []
        temp_default_code = [line.get(self._Titles['default_code'],'') for line in check_data if line]
        for line in temp_default_code:
            count = temp_default_code.count(line)
            if count > 1:
                err_check_default_code.append(line)
        if err_check_default_code:
            raise osv.except_osv(u"错误", u"下列内部编码重复 %s" % ''.join(err_check_default_code))
        product_create = []
        product_update = []
        res_ids = []
        product_create,product_update = self.isExsit(cr, uid, ids, context, data, action)

        #创建新的产品
        for line in product_create:
            id = product_obj.create(cr,uid,line,context)
            res_ids.append(id)
        
        if 'update' == action:
            for line in product_update:
                id = line.get('id',None)
                if id:
                    del line['id']
                    product_obj.write(cr,uid,id,line)
                    res_ids.append(id) 
        return {
            'name': u'产品导入结果',
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'product.template',
            "domain": [('id', 'in', res_ids)],
            'type': 'ir.actions.act_window',
        }
    
    def isExsit(self,cr,uid,ids,context=None,datas=[],action='create'):
        '''
        @note: 检测产品数据是否在系统中存在
        @param data: 产品数据
        @param action:操作类型：create update 
        @author: cloudy
        '''
        product_datas = datas['data']
        product_obj = self.pool.get('product.template')
        product_error = []
        product_create = []
        product_update = []
        for line in product_datas:
            product_name = line.get(self._Titles['name'],'')
            default_code = line.get(self._Titles['default_code'],'')
            default_code = unicodedata.normalize('NFKD', default_code).encode('ascii','ignore')
            sale_ok = line.get(self._Titles['sale_ok'],False)
            list_price = line.get(self._Titles['price'],'0')
            list_price = float(str(list_price))
            
            #判断产品的属性和属性值在系统中是否存在
            
            if not default_code:
                continue
            if not isinstance(default_code, basestring):
                raise osv.except_osv(u"错误", u"%s 必须为文本类型 "%self._Titles['default_code'])
            #检测内部编码在系统中是否存在
            ins_product = product_obj.search(cr,uid,[('default_code','=',default_code)])
            #如果系统中产品已经存在，判断动作为创建还是为更新，根据动作进行进一步操作
            if ins_product and 'create' == action:
                product_error.append({'name':product_name,'default_code':default_code})
            elif ins_product and 'update' == action:    
                id = ins_product and ins_product[0]
                product_update.append({
                    'id':id,
                    'name':product_name,
                    'active':True,
                    'type':'product',
                    'list_price':list_price,
                })  
               
            else:
                product_create.append({
                    'name':product_name,
                    'active':True,
                    'type':'product',
                    'default_code':default_code,
                    'list_price':list_price,
                })  
        if product_error:
            error_info = ''
            for line in product_error:
                error_info += '%s,'%line.get('default_code')
            raise osv.except_osv(u"错误", u"下面的内部编码重复:\n%s" % error_info)
        return   product_create,product_update
            
            
            
            
            
            
        
        
          
        


