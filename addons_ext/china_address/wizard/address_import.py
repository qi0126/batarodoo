# -*- coding: utf-8 -*-

from openerp.osv import fields,osv
import json
from openerp.tools.common_ext import ImportExcelFile

class address_import(osv.osv_memory):
    _name = 'address.import'
    _columns ={
        'file': fields.binary('excel File',help='select excel file',filter='*.xls|*.csv'),
    }
    _Titles = {'province':u'省','city':u'市','district':u'区'}
    def apply(self, cr, uid, ids, context=None):
        res_ids =[]
        province_obj = self.pool.get('res.country.state')
        city_obj = self.pool.get('res.country.state.city')
        district_obj = self.pool.get('res.country.state.city.district')
        wizard = self.browse(cr,uid,ids[0],context)
        data = ImportExcelFile(wizard.file).readFile()
        for line in data['data']:
            province = line.get(self._Titles['province'],'')
            city = line.get(self._Titles['city'],'')
            district = line.get(self._Titles['district'],'')
            #获取省份的前两个字
            province_alias = province[0:3]
            mm = "%s%s" %(province_alias,"%")
            province_id = province_obj.search(cr,uid,[('name','like',mm)])
            if not province_id:
                continue
            province_id = province_id and province_id[0]
            #判断城市是否存在
            city_id = city_obj.search(cr,uid,[('name','=',city)])
            if not city_id:
                city_id = city_obj.create(cr,uid, {'name':city,'province_id':province_id},context)
            else:
                city_id = city_id and city_id[0]
            #判断地区是否存在
            
            district_id = district_obj.search(cr,uid,[('name','=',district)])
            if not district_id:
                district_id = district_obj.create(cr,uid, {'name':district,'city_id':city_id},context)
            else:
                district_id = district_id and district_id[0]
            res_ids.append(district_id)
            #print 'district:',district
        return {
            'name': u'全国地址导入结果',
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'res.country.state.city.district',
            "domain": [('id', 'in', res_ids)],
            'type': 'ir.actions.act_window',
        }
            
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        