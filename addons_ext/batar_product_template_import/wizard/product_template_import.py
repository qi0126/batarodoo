#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:product_template_import.py
@date:2016/11/8 14:36
"""

from openerp.osv import fields,osv
from openerp.tools.common_ext import ImportExcelFile
import unicodedata

class product_template_import(osv.osv_memory):
    '''产品款式导入'''
    _name = 'product.template.import'
    _columns = {
        'file': fields.binary('Excel File', filter='*.xls|*.csv'),
        'action': fields.selection([('update', 'Update or Create'), ('create', 'Create')], string='import data action'),
    }
    _defaults = {
        'action': 'create',
    }
    _Titles = {
        'batar_product_category': u'饰品小类',
        'name': u'型号说明',
        'import_code': u'型号编号',
        'grade':u'含金量',
        'one': u'企业分类',
        'two': u'饰品中类',
        'three': u'饰品小类',

    }

    def apply(self, cr, uid, ids, context=None):
        """"""
        product_obj = self.pool.get('product.template')
        wizard = self.browse(cr, uid, ids[0], context)
        action = wizard.action
        excel_obj = ImportExcelFile(wizard.file)
        data = excel_obj.readFile()
        if not data:
            raise osv.except_osv(u"错误", u"文件读取失败" )
        # 对输入的数据进行查重
        check_data = data['data']
        err_check_import_code = []
        all_import_code_list = [line.get(self._Titles['import_code'], '')for line in check_data if line]

        import_code_list = []
        for line in all_import_code_list:
            if not line or (not line.strip()):
                continue
            import_code_list.append(line)
        if not import_code_list:
            raise  osv.except_osv(u"错误","导入的execl文件中没有“型号编号”对应的字段信息")
        for line in import_code_list:
            count = import_code_list.count(line)
            if count > 1:
                err_check_import_code.append(line)
        if err_check_import_code:
            raise osv.except_osv(u"错误", u"下列型号重复 %s" % ''.join(err_check_import_code))
        res_ids = []
        product_create, product_update = self.isExsit(cr, uid, ids, context, data,import_code_list, action)
        # 创建新的产品
        for line in product_create:
            id = product_obj.create(cr, uid, line, context)
            res_ids.append(id)
        for line in product_update:
            id = line.get('id', None)
            if id:
                del line['id']
                product_obj.write(cr, uid, id, line)
                res_ids.append(id)
        # if 'update' == action:
        #     for line in product_update:
        #         id = line.get('id', None)
        #         if id:
        #             del line['id']
        #             product_obj.write(cr, uid, id, line)
        #             res_ids.append(id)
        if not res_ids:
            raise osv.except_osv(u"错误", u"导入失败，请检查数据")
        return {
            'name': u'产品导入结果',
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'product.template',
            "domain": [('id', 'in', res_ids)],
            'type': 'ir.actions.act_window',
        }

    def isExsit(self,cr,uid,ids,context=None,datas=[],import_code_list=[],action='create'):
        """"""
        product_datas = datas['data']
        product_obj = self.pool.get('product.template')
        attribute_value_obj = self.pool.get('product.attribute.value')
        product_create = []
        product_update = []
        product_error = []
        material_dict = {}
        category_name_dict = {}
        for line in product_datas:
            product_name = line.get(self._Titles['name'], '')
            product_name = product_name.strip()
            one_name = line.get(self._Titles['one'], '')
            two_name = line.get(self._Titles['two'], '')
            three_name = line.get(self._Titles['three'], '')
            one_name = one_name.strip()
            two_name = two_name.strip()
            two_name = two_name.strip()
            category_name = ""
            if not three_name:
                category_name = three_name
            elif not two_name:
                category_name = two_name
            elif not one_name:
                category_name = one_name
            category_name_id = ""
            if category_name:
                category_name_id = category_name_dict.get(category_name,"")
                if not category_name_id:
                    cate_obj_id = self.pool.get('batar.product.category').search(cr,uid,[('name','=',category_name)])
                    if cate_obj_id:
                        category_name_id = cate_obj_id[0]
                        category_name_dict[category_name] = category_name_id
                    else:
                        raise osv.except_osv(u"错误", u"企业分类 %s 不存在，请先导入或者创建"  % category_name)
            import_code = line.get(self._Titles['import_code'], '')
            if isinstance(import_code,str):
                pass
            else:
                import_code = unicodedata.normalize('NFKD', import_code).encode('ascii', 'ignore')
            # 检测内部编码在系统中是否存在
            if import_code not in import_code_list:
                continue
            ins_product = product_obj.search(cr, uid, ["|",('import_code', '=', import_code),('name','=',product_name)])
            # 如果系统中产品已经存在，判断动作为创建还是为更新，根据动作进行进一步操作
            # if ins_product and 'create' == action:
            #     product_error.append({'name': product_name, 'import_code': import_code})
            # elif ins_product and 'update' == action:
            #     id = ins_product and ins_product[0]
            #     product_update.append({
            #         'id': id,
            #         'name': product_name,
            #         'active': True,
            #         'type': 'product',
            #         'sale_ok':True,
            #         'import_code': import_code,
            #
            #     })

            if ins_product:
                id = ins_product and ins_product[0]
                product_update.append({
                    'id': id,
                    'import_code': import_code,

                })

            else:
                grade = line.get(self._Titles['grade'],"")
                attribute_line_ids = []
                material_id = \
                self.pool.get('ir.model.data').get_object_reference(cr,uid,'product_info_extend', 'product_attribute_material')[1]
                if grade == "AU999":
                    search_name= u'足金999'
                    val_id = material_dict.get(search_name,'')
                    if not val_id:
                        attribute_value = attribute_value_obj.search(cr,uid,[('attribute_id','=',material_id),('name','=',search_name)])

                        if attribute_value:
                            material_dict[grade] =attribute_value[0]
                            val_id = attribute_value[0]
                        else:
                            raise osv.except_osv(u"错误", u"下面的材质不存在:\n%s" % grade)
                    attribute_line_ids = [(0,0,{'attribute_id':material_id,'value_ids':[(6,0,[val_id])]})]
                value = {
                    'name': product_name,
                    'active': True,
                    'sale_ok': True,
                    'type': 'product',
                    'import_code': import_code,
                }
                if category_name_id:
                    value['batar_cate_id'] = category_name_id
                if attribute_line_ids:
                    value['attribute_line_ids'] = attribute_line_ids
                product_create.append(value)

        if product_error:
            error_info = ''
            for line in product_error:
                error_info += '%s,'%line.get('import_code')
            # raise osv.except_osv(u"错误", u"下面的导入编码重复:\n%s" % error_info)
        return product_create,product_update