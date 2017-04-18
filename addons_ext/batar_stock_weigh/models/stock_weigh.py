#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:stock_weigh.py
@date:2016/11/1 17:08
"""
from openerp import  models,api
from openerp.exceptions import UserError
import urllib
import urllib2


class stock_weigh(models.Model):
    ''''''
    _name = 'stock.weigh'
    _STATE = {
        'draft':u"草稿",
        'confirm':u"确认",
        'wait_check':u"等待质检",
        'done':u"质检完成"
    }
    @api.model
    def pick_in_order_weigh_done(self,lineId="" ,netWeight=0,grossWeight=0,Qty=0):
        """写入分盘称重信息"""
        if not lineId :
            return "failed"
        pick_in_order_line_obj = self.env['stock.pick.in.order.line']
        order_line = pick_in_order_line_obj.search([('id','=',lineId)])
        plate_id = self.env['quality.plate'].search([('user_id','=',self.env.uid),('state','=','draft')])
        values = {}
        line = self.env['stock.pick.in.order.line'].search([('plate_id', '=', plate_id.id)], order='sequence desc', limit=1)
        if order_line:
            if not order_line.plate_id:
                values['plate_id'] = plate_id.id
                if line:
                    values['sequence'] = line.sequence + 1
                else:
                    values['sequence'] = 1
            values['state'] = 'wait_pick_in'

            values["actual_product_qty"] = Qty
            values["actual_net_weight"] = netWeight
            values["ctual_gross_weight"] = grossWeight
            order_line.write(values)
        else:
            return 'failed'
        return 'success'
    @api.model
    def search_pick_in_order_package(self,package_number=""):
        res = {
            'code': 'failed',
            'data': {},
            'message': '',
        }
        if not package_number:
            return res
        search_list = [('name', '=', package_number), ('state', '=', 'wait_split'),('plate_id','=',None)]
        stock_pick_in_order_line = self.env['stock.pick.in.order.line'].search(search_list, limit=1)
        if stock_pick_in_order_line:
            info = {
                'package_num': stock_pick_in_order_line.name,
                'id': stock_pick_in_order_line.id,
                'product_name': stock_pick_in_order_line.product_id.name + stock_pick_in_order_line.product_id.string_attribute,
                'default_code': stock_pick_in_order_line.product_id.default_code,
                'product_qty': stock_pick_in_order_line.product_qty,
                'net_weight': stock_pick_in_order_line.net_weight,
                'gross_weight': stock_pick_in_order_line.gross_weight,
                'actual_product_qty': stock_pick_in_order_line.actual_product_qty,
                'actual_net_weight': stock_pick_in_order_line.actual_net_weight,
                'actual_gross_weight': stock_pick_in_order_line.actual_gross_weight,
            }
            # if stock_pick_in_order_line.product_id.
            if info:
                res['data'] = info
                res['code'] = 'success'
        return  res

    @api.model
    def pick_weigh_done(self,lineId="" ,netWeight=0,grossWeight=0):
        """写入分拣包重量信息"""
        if not lineId :
            return "failed"
        batar_package_obj = self.env['batar.package']
        batar_package = batar_package_obj.search([('id','=',lineId)])
        if batar_package:
            batar_package.net_weight = netWeight
            batar_package.weight = grossWeight
            batar_package.state ="done"
        else:
            return 'failed'
        return 'success'
    @api.model
    def search_pick_out_package(self,package_number=""):
        """搜索分拣包"""
        res = {
            'code': 'failed',
            'data': {},
            'message': '',
        }
        if not package_number:
            return res
        search_list = [('name','=',package_number)]
        batar_package_obj = self.env['batar.package']
        batar_package = batar_package_obj.search(search_list,limit=1)
        if not batar_package:
            return res
        data = {
            'id': batar_package.id,
            'name':batar_package.name or "-",
            'partner_name':batar_package.partner_id.name or "-",
            'product_code':batar_package.product_code,
            'product_name':batar_package.product_id.name+batar_package.product_id.string_attribute,
            'qty':batar_package.qty,
            'weight':batar_package.weight,
            'net_weight':batar_package.net_weight,
        }
        res['data'] =data
        res['code']='success'
        return  res

    @api.model
    def search_quality_package(self,package_number=""):
        """搜索质检包"""
        res = {
            'code':'failed',
            'data':[],
            'message':'',
        }
        if not package_number:
            return res
        search_list = [('name','=',package_number),('state','=','wait_check')]
        quality_order_line = self.env['quality.order.line'].search(search_list,limit=1)
        quality_order_line_list = []

        if quality_order_line:
            quality_order_line_list.append({
                'package_num' : quality_order_line.name,
                'id':quality_order_line.id,
                'product_name':quality_order_line.product_id.name+quality_order_line.product_id.string_attribute,
                'default_code':quality_order_line.product_id.default_code,
                'product_qty':quality_order_line.product_qty,
                'net_weight':quality_order_line.net_weight,
                'gross_weight':quality_order_line.gross_weight,
                'state':self._STATE.get(quality_order_line.state,u"异常"),
            })
            res['code']='success'
            res['data'] = quality_order_line_list
        return res
    @api.model
    def change_plate(self):
        '''换盘'''
        plate = self.env['quality.plate'].search([('state','=','draft'),('user_id', '=', self.env.uid)])
        if plate:
            if not plate.line_ids:
                raise UserError(u"盘号:%s为空盘，不能换盘" % plate.name)
            plate.state='wait_pick_in'

        #创建新盘
        obj = self.env['quality.plate'].search([],order="id desc",limit=1)
        name = 1
        if obj:
            name = int(obj.name) + 1
        self.env['quality.plate'].create({
            'user_id': self.env.uid,
            'state': 'draft',
            'name':"%s" % name
        })
        return name
    @api.model
    def get_plate(self):
        """获得当前盘号"""
        plate = self.env['quality.plate'].search([('state', '=', 'draft'), ('user_id', '=', self.env.uid)])
        if plate :
            return plate.name
        else:
             return ""
    @api.model
    def split_plate_done(self):
        plate = self.env['quality.plate'].search([('state', '=', 'draft'), ('user_id', '=', self.env.uid)])
        if plate:
            if not plate.line_ids:
                raise UserError(u"盘号:%s为空盘，无法完成分盘"%plate.name)
            plate.state = 'wait_pick_in'
        else:
            raise UserError(u"无未完成的盘")
        return ""

    @api.model
    def get_serial_data(self,Url=""):
        """"""
        response_dict = {
            'code': '500',
            'data': 0,
            'msg': '',
        }
        if not Url:
            return response_dict
        try:
            req = urllib2.Request(Url)

            res_data = urllib2.urlopen(req)
            response_dict = res_data.read()
        except:
            pass
        return response_dict
    @api.model
    def quality_check_ok(self, pakeNum= "" ,lines=[]):
        """质检通过保存记录"""
        if not pakeNum:
            return 'failed'
        quality_order_line = self.env['quality.order.line'].search([('name','=',pakeNum)],limit=1)
        if not quality_order_line:
            return 'failed'
        check_records = []
        for line in lines:
            values = {
                'check_user':self.env.uid,
                'order_line_id':quality_order_line.id,
                'supplier_code':quality_order_line.supplier_code,
                'default_code':quality_order_line.product_id.id,
                'product_qty':line.get('qty',0),
                'net_weight':line.get('net_weight',0),
                'gross_weight':line.get('gross_weight',0),
                'ok': True,

            }
            if line.get('reason',0):
                values['reason'] = int(line.get('reason',0))
            check_records.append((0,0,values))
        quality_order_line.quality_id.write({
            'check_ids':check_records,
            'check_user': self.env.uid,
        })
        quality_order_line.ok = True
        quality_order_line.state = 'checked'

        return 'success'

    @api.model
    def quality_check_not(self, pakeNum="", lines=[]):
        """质检不通过保存记录"""
        if not pakeNum:
            return 'failed'
        quality_order_line = self.env['quality.order.line'].search([('name','=',pakeNum)],limit=1)
        if not quality_order_line:
            return 'failed'
        check_records = []
        for line in lines:
            values = {
                'check_user':self.env.uid,
                'quality_id':quality_order_line.quality_id.id,
                'order_line_id':quality_order_line.id,
                'supplier_code':quality_order_line.supplier_code,
                'default_code':quality_order_line.product_id.id,
                'product_qty': line.get('qty', 0),
                'net_weight': line.get('net_weight', 0),
                'gross_weight': line.get('gross_weight', 0),
                'ok': False,
            }
            if line.get('reason',0):
                values['reason'] = int(line.get('reason',0))
            check_records.append((0,0,values))
        quality_order_line.quality_id.write({
            'check_ids':check_records,
            'check_user':self.env.uid,
        })
        quality_order_line.ok = False
        quality_order_line.state = 'checked'

        return 'success'
    @api.model
    def get_quality_reason(self):
        """获得质检原因"""
        res = {
            'code': 'failed',
            'data': [],
            'message': '',
        }
        reasons = self.env['quality.reason'].search([])
        data = []
        for reason in reasons:
            data.append({
                'id':reason.id,
                'name':reason.name
            })
        if data:
            res['code'] = 'success'
            res['data'] = data
        return res
