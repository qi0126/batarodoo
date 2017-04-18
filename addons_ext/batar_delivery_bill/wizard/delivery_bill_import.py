# -*- coding: utf-8 -*-


from openerp import api, fields,models,_
from ..utils import deliveryExcelAction
from openerp.exceptions import UserError

 
class delivery_bill_import(models.TransientModel):
    _name = 'delivery.bill.import'
    
#     _columns = {
#         'file': fields.binary('excel File',help='order info file',filter='*.xls|*.csv'),
#     }
#     
    file = fields.Binary(string='delivery bill import file')
    line = fields.Integer(string='line start',default=7)
    sheet = fields.Integer(string='',default=0)
    @api.multi
    def apply(self):
        '''导入文件'''
       
        exceObj = deliveryExcelAction.deliveryExcelFile(file_contents=self.file,line=self.line,sheet= self.sheet)
        data_dict = exceObj.readFile()
        
        if data_dict is None:
            raise UserError(_(u"导入失败，文档中有些数据不支持！")) 
        #数据处理
        values = {}
        
        values['charge_man'] = self.env.uid
        values['name']= data_dict['name']
        values['partner_person'] = data_dict['partner_person']
        partner_name = data_dict['partner_name']
        partner_id = self.env['res.partner'].search([('name','=',partner_name)])
        if partner_id:
            values['partner_id'] = partner_id.id
        values['partner_mobile'] = data_dict['partner_mobile']
        values['delivery_method'] = data_dict.get('delivery_method','')
        values['delivery_man'] = data_dict.get('delivery_man','')
        values['delivery_mobile'] = data_dict['delivery_mobile']
        location_src_id = self.env['stock.location'].search([('usage','=','supplier')],limit=1)
        if location_src_id:
            values['location_src_id'] = location_src_id.id
        obj = self.env['stock.picking.type'].search([('code','=','incoming')],limit=1,order="id")
        if obj:
            values['location_dest_id'] =  obj.default_location_dest_id.id
        data_lines = data_dict['data']
        pkg_line = []
        err_line  =[]
        no_default_code =[]
        data_len = len(data_lines)
        for i in range(data_len):
            line = data_lines[i]
            default_code = line.get(u'尚金缘产品编号','')
            default_code = str(default_code).strip()
            if default_code:
                packing_code = str(line.get(u'包装码','')).strip()
                parent_pkg_number = str(line.get(u'父包号','')).strip()
                pkg_number = str(line.get(u'包号','')).strip()
                value_lines = {
                    'purchase_number':line.get(u'采购单号',''),
                    'packing_code':packing_code,
                    'parent_pkg_number':parent_pkg_number,
                    'pkg_number':pkg_number,
                    'supplier_code':line.get(u'供应商产品编号',''),
                    'default_code':default_code,
                    'product_qty':line.get(u'件数',0),
                    'net_weight':line.get(u'净重',0),
                    'gross_weight':line.get(u'毛重',0)  
                }
                product_obj = self.env['product.product'].search([('default_code','=',default_code)])
                if product_obj:
                    value_lines['product_id'] = product_obj.id
                else:
                    err_line.append(default_code)
                    
                pkg_line.append((0,0,value_lines))
            else:
                no_default_code.append(str(self.line+i+1))
        if err_line:
            raise UserError(_(u'下面尚金缘编码在系统中不存在:%s'% ','.join(err_line)))
        if no_default_code:
            raise UserError(_(u'下面行尚金缘编码不存在:%s'% ','.join(no_default_code)))
        values['line_id'] = pkg_line
        obj = self.env['delivery.bill'].create(values)
        id =None or obj.id 
        return {
                'name': _(u'送货单导入结果'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'delivery.bill',
                "domain": [('id', '=', id)],
                'type': 'ir.actions.act_window',
            }
                    
