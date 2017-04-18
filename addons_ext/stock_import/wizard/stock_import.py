# -*- coding: utf-8 -*-

from openerp.osv import fields,osv
from openerp.tools.common_ext import ImportExcelFile

class stock_import(osv.osv_memory):
    _name = 'stock.import'
    _columns = {
        'file': fields.binary('excel File',help='order info file',filter='*.xls|*.csv'),
        'action':fields.selection([('update','update or create'),('create','create')],string='data action'),
        'location_id':fields.many2one('stock.location',string='stock warehouse'),
        'name':fields.char(size=50,string='stock inventory name')
    }
    _Titles = {'warehouse':u'库位','ean13':u'产品编码','default_code':u'内部编码','virtual':u'理论数量','actual':u'实际数量'}
    
    def checkProdcutExsit(self, cr, uid, ids,context=None,default_code=''):
        '''检查产品在系统中是否存在
        @param default_code:产品内部编码，非产品条码
         '''
        if not default_code:
            return False
        product_obj = self.pool.get('product.product')
        product = product_obj.search(cr,uid,[('default_code','=',default_code)])
        if product:
            return product and product[0]
        else:
            return False
    
    def apply(self, cr, uid, ids, context=None):
        '''将库存盘点数据导入到系统中'''
        wizard = self.browse(cr, uid, ids[0], context)
        exceObj = ImportExcelFile(wizard.file)
        data = exceObj.readFile()
        stock_obj = self.pool.get('stock.inventory')
        stock_line_obj = self.pool.get('stock.inventory.line')
        stock_data = data['data']
        name =""
        location_id = wizard.location_id.id
        val = {
            'name':name,
            'location_id':location_id,
            'filter':'none',
            'state':'confirm',
        }
        stock_line = []
        inventory_id = stock_obj.create(cr,uid,val,context)
#         print inventory_id
        product_not_exsit = []
        for line in stock_data:
            default_code = line.get(self._Titles.get('default_code'),'')
            if not isinstance(default_code, basestring):
                raise osv.except_osv(u"错误", u"%s 必须为文本类型 "%self._Titles['default_code'])
            product_id = self.checkProdcutExsit(cr, uid, ids, context, default_code)
            if not product_id:
                product_not_exsit.append(default_code)
                continue
            line_val = {
                'location_id':location_id,
                'product_id':product_id,
                'product_qty':line.get(self._Titles['actual'],0),
                'inventory_id':inventory_id,
            }
            stock_line.append(line_val)
        if product_not_exsit:
            error_info = ''
            for line in product_not_exsit:
                error_info += '%s,'%line
            raise osv.except_osv(u"错误", u"下列内部编码在系统中不存在:\n%s" % error_info)
#         print stock_line
        for line in stock_line:
            stock_line_obj.create(cr,uid,line,context)
        return {
            'name': u'库存导入结果',
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'stock.inventory',
            "domain": [('id', 'in', [inventory_id])],
            'type': 'ir.actions.act_window',
        }
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 