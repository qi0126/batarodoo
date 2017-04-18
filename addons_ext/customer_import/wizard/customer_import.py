# -*- coding: utf-8 -*-
'''
Created on 2016年1月14日

@author: cloudy
'''

from openerp.osv import fields,osv
from openerp.tools.common_ext import ImportExcelFile
import unicodedata



class customer_import(osv.osv_memory):
    _name ="customer.import"
    _columns = {
        'file':fields.binary('Excel File',filter='*.xls|*.csv'),
        'action':fields.selection([('update','Update or Create'),('create','Create')],string='import data action'),
    }
    _defaults = {
        'action':'create',
    }
    _Titles = {
        'name':u'客户名称',
        'customer_code':u'客户编码',
        'is_company':u'是公司'
    }
    def apply(self,cr,uid,ids,context=None):
        '''导入客户信息'''
        customer_obj = self.pool.get('res.partner')
        wizard = self.browse(cr, uid, ids[0], context)
        action= wizard.action
        excel_obj = ImportExcelFile(wizard.file)
        data = excel_obj.readFile()
        #对输入的数据进行查重
        check_data = data['data']
        err_check_customer_code = []
        customer_code = [line.get(self._Titles['customer_code'],'') for line in check_data if line]
        for line in customer_code:
            count = customer_code.count(line)
            if count > 1:
                err_check_customer_code.append(line)
            
        if err_check_customer_code:
            raise osv.except_osv(u"错误", u"下列客户编码重复 %s" % ''.join(err_check_customer_code))
        customer_create = []
        customer_update = []
        res_ids = []
        customer_create,customer_update = self.isExsit(cr, uid, ids, context, data, action)
        
        #新建客户
        for line in customer_create:
            id =customer_obj.create(cr,uid,line,context)
            res_ids.append(id)
        if 'update' == action:
            for line in customer_update:
                id = line.get('id',None)
                if id:
                    del line['id']
                    customer_obj.write(cr,uid,id,line)
                    res_ids.append(id)
        return {
            'name': u'客户导入结果',
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'res.partner',
            "domain": [('id', 'in', res_ids)],
            'type': 'ir.actions.act_window',
        }
        
    def isExsit(self,cr,uid,ids,context=None,datas=[],action='create'):
        '''根据客户编码检测客户是否存在'''
        customer_datas = datas['data']
        customer_obj = self.pool.get('res.partner')
        customer_error =[]
        customer_create = []
        customer_update = []
        for line in customer_datas:
            customer_name= line.get(self._Titles['name'],'')
            customer_code = line.get(self._Titles['customer_code'])
            customer_code = unicodedata.normalize('NFKD', customer_code).encode('ascii','ignore')
            is_company = line.get(self._Titles['is_company'],0)
            try:
                is_company = int(is_company)
                is_company = is_company and True
            except:
                raise osv.except_osv(u"错误", u"客户编码为:%s的\"是公司\"列 不为整数" % (customer_code))
            #检测客户在系统中是否存在，根据客户编码，不根据客户名称
            ins_customer = customer_obj.search(cr,uid,[('customer_code','=',customer_code)])
            if ins_customer and 'create' == action:
                customer_error.append({'name':customer_name,'customer_code':customer_code})
            elif ins_customer and 'update' == action:
                id = ins_customer and ins_customer[0]
                customer_update.append({
                    'id':id,
                    'name':customer_name,
                    'customer_code':customer_code,
                    'is_company':is_company,
                })
            else:
                customer_create.append({
                    'name':customer_name,
                    'customer_code':customer_code,
                    'is_company':is_company,
                })
        if customer_error:
            error_info = ''
            for line in customer_error:
                error_info += '%s,'%line.get('customer_code')
            raise osv.except_osv(u"错误", u"下面的客户编码重复:\n%s" % error_info)
        return   customer_create,customer_update
                
        
        