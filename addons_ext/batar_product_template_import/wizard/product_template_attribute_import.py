#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:product_template_attribute_import.py
@date:2016/11/9 11:20
"""
from openerp.osv import fields,osv
from openerp.tools.common_ext import ImportExcelFile
import unicodedata

class product_template_attribute_import(osv.osv_memory):
    _name = 'product.template.attribute.import'

    name = 'product.template.import'
    _columns = {
        'file': fields.binary('Excel File', filter='*.xls|*.csv'),
        'attribute_id':fields.many2one('product.attribute',string='product attribute')
    }

    _Titles = {
        'import_code': u'型号编号',
        'attribute_value':u"属性值"
    }
    def apply(self, cr, uid, ids, context=None):
        """"""
        product_obj = self.pool.get('product.template')
        wizard = self.browse(cr, uid, ids[0], context)
        attribute_id = wizard.attribute_id.id
        excel_obj = ImportExcelFile(wizard.file)
        data = excel_obj.readFile()
        if not data:
            raise osv.except_osv(u"错误", u"文件读取失败" )
        # 对输入的数据进行查重
        check_data = data['data']
        err_check_import_code = []
        res_ids = []
        product_dict = {}
        for line in check_data:
            import_code = line.get(self._Titles['import_code'], '')
            attribute_value = line.get(self._Titles['attribute_value'], '')
            # if isinstance(import_code,str):
            #     pass
            # else:
            #     import_code = unicodedata.normalize('NFKD', import_code).encode('ascii', 'ignore')
            attribute_value = "%s" % attribute_value
            if product_dict.get(import_code,""):
                product_dict[import_code].append(attribute_value)
            else:
                product_dict[import_code] = [attribute_value]
        import_code_list = product_dict.keys()

        attribute_dict = {}
        for import_code in import_code_list :
            if not import_code:
                continue
            product_template_id = product_obj.search(cr, uid, [('import_code', '=', import_code)])
            if not product_template_id:
                continue
            product_template_id = product_template_id[0]
            product_template = product_obj.browse(cr, uid, product_template_id, context={})
            res_ids.append(product_template.id)
            attribute_line_ids = product_template.attribute_line_ids
            product_attribute_ids = []
            product_attribute_line_id_dict = {}
            for attribute_line_id in attribute_line_ids:
                product_attribute_ids.append(attribute_line_id.attribute_id.id)
                for j in attribute_line_id.value_ids:
                    product_attribute_line_id_dict[j.attribute_id.id] = attribute_line_id.id

            if attribute_id in product_attribute_ids:
                value_id_list = []

                for attribute in product_dict[import_code]:

                    if wizard.attribute_id.code =='weight':
                        attribute = "%sg"%attribute
                    value_id = self.pool.get('product.attribute.value').search(cr, uid, [('name', '=', attribute), (
                    'attribute_id', '=', attribute_id)])
                    value_id = value_id and value_id[0]
                    if not value_id:
                        print attribute_id,"==",attribute,'=='
                        value_id = self.pool.get('product.attribute.value').create(cr, uid, {'name': attribute,'attribute_id': attribute_id})
                    attribute_dict[attribute] = value_id
                    value_id_list.append(value_id)
                line_id = product_attribute_line_id_dict.get(attribute_id,"")
                if line_id:
                    product_obj.write(cr, uid, product_template.id, {
                    'attribute_line_ids':[(1,line_id,{'value_ids':[(6,0,value_id_list)]})]
                    })
            else:
                value_id_list = []
                for attribute in product_dict[import_code]:
                    if wizard.attribute_id.code =='weight':
                        attribute = "%sg"%attribute
                    value_id = self.pool.get('product.attribute.value').search(cr, uid, [('name', '=', attribute),('attribute_id', '=',attribute_id)])
                    value_id = value_id and value_id[0]
                    if not value_id:
                        value_id = self.pool.get('product.attribute.value').create(cr,uid,{'name':attribute,'attribute_id':attribute_id})
                    attribute_dict[attribute] = value_id
                    value_id_list.append(value_id)
                product_obj.write(cr, uid, product_template.id, {
                    'attribute_line_ids':[(0,0,{'attribute_id':attribute_id,'value_ids':[(6,0,value_id_list)]})]
                })
        if not res_ids:
            raise osv.except_osv(u"错误", u"导入失败，请检查数据")
        return {
            'name': u'产品属性导入结果',
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'product.template',
            "domain": [('id', 'in', res_ids)],
            'type': 'ir.actions.act_window',
        }
