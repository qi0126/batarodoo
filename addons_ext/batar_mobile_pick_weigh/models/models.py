# -*- coding: utf-8 -*-

from openerp import  models,api

class pick_stock_weigh(models.Model):
    """入库拆包称重"""
    _name = 'pick.stock.weigh'
    @api.model
    def search_pick_package(self,pageNum=""):
        res = {
            'code': 'failed',
            'data': [],
            'message': '',
        }
        if not pageNum:
            return  res
        obj = self.env['batar.input.line']
        lines = obj.search([('package','=',pageNum), ('state', 'in', ('split','weight'))])
        data_list = []
        for line in lines:
            data_list.append({
                'id':line.id,
                'package':line.package,
                'product_code':line.product_id.default_code,
                'product_name':line.product_id.name+line.product_id.string_attribute,
                'qty':line.qty,
                'net_weight':line.net_weight,
                'location_id':line.location_id.name or '-',
                'split_sequence':line.split_sequence or '-',
                'src_location':line.src_location,
                'sequence':line.sequence or '-',
            })
        if data_list:
            res['data'] = data_list
            res['code'] = 'success'
        return res
    @api.model
    def write_weight_info(self,param={}):
        """写入称重信息"""
        if not param:
            return 'failed'
        obj = self.env['batar.input.line']
        ids = param.keys()
        one_line = ""
        for id in ids:
            line = obj.search([('id','=',id)])
            if not one_line:
                one_line = line
            if line.state == 'split' or line.state == 'weight':
                line.net_weight = param[id]
                if line.uom_id.name == 'g' or line.uom_id.name == 'kg':
                    line.qty = param[id]
                line.state = 'weight'

        if one_line:
            all_lines = one_line.input_id.line_ids
            states = [line.state for line in all_lines if line.state != "putaway"]
            need_write = [line for line in all_lines if line.state != "putaway"]
            states = list(set(states))
            if states == ['weight']:
                for line in need_write:
                    line.write({'state':'draft'})
        return 'success'
