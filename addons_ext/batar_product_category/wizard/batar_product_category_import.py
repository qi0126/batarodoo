#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:batar_product_category_import.py
@date:2016/11/9 10:29
"""
from openerp.osv import fields,osv
from openerp.tools.common_ext import ImportExcelFile
import unicodedata

class batar_product_category_import(osv.osv_memory):
    _name = 'batar.product.category.import'
    _columns = {
        'file': fields.binary('Excel File', filter='*.xls|*.csv'),
        'action': fields.selection([('update', 'Update or Create'), ('create', 'Create')], string='import data action'),
    }
    _defaults = {
        'action': 'create',
    }
    _Titles = {
        'one': u'企业分类',
        'two': u'饰品中类',
        'three': u'饰品小类',
    }
    def apply(self,cr,uid,ids,context=None):
        """"""
        batar_product_category_obj = self.pool.get('batar.product.category')
        wizard = self.browse(cr, uid, ids[0], context)
        excel_obj = ImportExcelFile(wizard.file)
        data = excel_obj.readFile()
        # 对输入的数据进行查重

        if not data:
            raise osv.except_osv(u"错误", u"文件读取失败" )
        category_dict = {}
        product_datas = data['data']


        for line in product_datas:
            one_name = line.get(self._Titles['one'], '')
            two_name = line.get(self._Titles['two'], '')
            three_name = line.get(self._Titles['three'], '')
            one_name = one_name.strip()
            two_name = two_name.strip()
            two_name = two_name.strip()
            if one_name:
                product_category_list = batar_product_category_obj.search(cr,uid,[('name','=',one_name)])
                if product_category_list:
                    category_dict[one_name] = product_category_list[0]
                else:
                    category_dict[one_name] = batar_product_category_obj.create(cr,uid,{'name':one_name})
            if two_name:
                product_category_list = batar_product_category_obj.search(cr,uid,[('name','=',two_name)])
                if product_category_list:
                    category_dict[two_name] = product_category_list[0]
                else:
                    values = {'name':two_name}
                    if one_name:
                        values['parent_id'] = category_dict[one_name]
                    category_dict[two_name] = batar_product_category_obj.create(cr,uid,values)

            if three_name:
                product_category_list = batar_product_category_obj.search(cr,uid,[('name', '=', three_name)])
                if product_category_list:
                    category_dict[three_name] = product_category_list[0]
                else:
                    values = {'name': three_name}
                    if two_name:
                        values['parent_id'] = category_dict[two_name]
                    category_dict[three_name] = batar_product_category_obj.create(cr,uid,values)
        return {
            'name': u'产品导入结果',
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'batar.product.category',
            "domain": [('id', 'in', category_dict.values())],
            'type': 'ir.actions.act_window',
        }
