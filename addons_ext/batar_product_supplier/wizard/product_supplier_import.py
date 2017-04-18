#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:product_supplier_import.py
@date:2016/11/10 16:42
"""
from openerp.osv import fields,osv
from openerp.tools.common_ext import ImportExcelFile
import unicodedata

class product_supplier_import(osv.osv_memory):
    _name = 'product.supplier.import'
    _columns = {
        'file': fields.binary('Excel File', filter='*.xls|*.csv'),
        'action': fields.selection([('update', 'Update or Create'), ('create', 'Create')], string='import data action'),
    }
    _defaults = {
        'action': 'create',
    }
    _Titles = {

        'name': u'型号说明',
        'import_code': u'型号编号',
        'supplier_name': u'生产工厂',

    }

    def apply(self, cr, uid, ids, context=None):
        """"""
        product_template_obj = self.pool.get('product.template')
        product_product_obj = self.pool.get('product.product')
        product_supplier_obj = self.pool.get('product.supplier')
        wizard = self.browse(cr, uid, ids[0], context)
        action = wizard.action
        excel_obj = ImportExcelFile(wizard.file)
        data = excel_obj.readFile()
        # 对输入的数据进行查重
        excel_data = data['data']
        res_ids = []
        supplier_dict= {}
        for line in excel_data:
            product_name = line.get(self._Titles['name'], '')
            import_code = line.get(self._Titles['import_code'], '')
            supplier_name = line.get(self._Titles['supplier_name'], '')
            if isinstance(import_code,str):
                pass
            else:
                import_code = unicodedata.normalize('NFKD', import_code).encode('ascii', 'ignore')
            if not import_code:
                continue
            supplier_id = supplier_dict.get(supplier_name,"")
            if not supplier_id:
                supplier_id = self.pool.get('res.partner').search(cr,uid,[('name','=',supplier_name),('supplier','=',True)])
                supplier_id = supplier_id and supplier_id[0]
            if not supplier_id:
                supplier_id =  self.pool.get('res.partner').create(cr,uid,{
                    'name':supplier_name,
                    'supplier':True,
                    'customer':False,
                    'is_company':True,
                })

                if not supplier_id:
                    continue
                supplier_dict[supplier_name] = supplier_id

            product_template_id = product_template_obj.search(cr,uid,[('import_code','=',import_code)])
            if not  product_template_id:
                continue
            product_ids = product_product_obj.search(cr,uid,[('product_tmpl_id','in',product_template_id)])
            for product_id in product_ids:
                id = product_supplier_obj.create(cr,uid,{
                    'product_id':product_id,
                    'partner_id':supplier_id,
                    'supplier_product_code':import_code,
                    'supplier_product_name':product_name,
                    'min_qty':1,
                    'uom_id': self.pool.get('ir.model.data').get_object_reference(cr,uid,'product', 'product_uom_unit')[1]
                })
                if id:
                    res_ids.append(id)
        return {
            'name': u'产品供应商导入结果',
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'product.supplier',
            "domain": [('id', 'in', res_ids)],
            'type': 'ir.actions.act_window',
        }