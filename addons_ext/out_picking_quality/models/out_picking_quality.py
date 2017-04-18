# -*- coding: utf-8 -*-

from openerp import models, fields, api

class out_picking_quality(models.Model):
    _name = 'out.picking.quality'

    _order_line_state = {
        'draft': u"草稿",
        'wait': u"等待质检",
        'ok': u"质检通过" ,
        'has_back_or_exchange':u"存在退换货",
        'done': u"完成"
    }
    user_id = fields.Many2one('res.users', string='user')
    current_customer = fields.Many2one('res.partner', string='current customer')
    last_customer = fields.One2many('last.check.customer', 'record_id', string='last check customer')
    order_id = fields.Many2one('out.quality.order', string='out quality order')

    @api.model
    def get_current_customer_all_wait_order(self):
        """获得当前客户所有待验订单"""
        res = {
            'code': 'failed',
            'data': [],
            'message': u"没有符合要求的数据"
        }
        out_picking_quality = self.env['out.picking.quality'].search([('user_id', '=', self.env.uid)])
        customer = out_picking_quality.current_customer
        if customer:
            out_quality_orders = self.env['out.quality.order'].search([('state', '!=', 'done'), ('partner_id', '=', customer.id)])
            data_list = []
            for line in out_quality_orders:
                data_list.append({
                    'id': line.id,
                    'name': line.name,
                    "pick_user": (line.pick_user and line.pick_user.name) or "",
                    'customer': (line.partner_id and line.partner_id.name) or ""
                })
            if data_list:
                res['code'] = 'success'
                res['data'] = data_list
        return res

    @api.model
    def quality_order_check_weight_done(self, line_id='', check_weight=0, back_qty=0, exchange_qty=0,back_weight=0):
        """称重结果写入"""
        check_weight = float(check_weight)
        back_qty = float(back_qty)
        exchange_qty = float(exchange_qty)
        back_weight = float(back_weight)
        if not line_id:
            return 'failed'
        line_obj = self.env['out.quality.order.line'].search([('id', '=', line_id)])
        if line_obj:
            state = 'ok'
            if int(float(back_qty)*100) > 0 or int(float(exchange_qty)*100) > 0:
                state = 'has_back_or_exchange'
            back_qty = back_qty+exchange_qty
            if int(float(line_obj.qty)*100)  >= int(float(back_qty)*100):
                line_values = {
                    'check_weight': check_weight,
                    'back_qty': 0,
                    'exchange_qty': 0,
                    'back_weight': 0,
                    'qty': line_obj.qty - back_qty,
                    'state': state
                }
                if back_qty>0:
                    back_values = {
                        "order_line":line_obj.id,
                        'quality_order': line_obj.quality_order_id.id,
                        'product_id':line_obj.product_id.id,
                        'qty':back_qty,
                        'net_weight':back_weight,
                        'check_user_id':self.env.uid
                    }
                    line_values['back_lines']=[(0,0,back_values)]
                if exchange_qty>0:
                    exchange_values = {
                        "order_line": line_obj.id,
                        'quality_order': line_obj.quality_order_id.id,
                        'product_id': line_obj.product_id.id,
                        'qty': exchange_qty,
                        'check_user_id': self.env.uid
                    }
                    line_values['exchange_lines'] = [(0, 0, exchange_values)]
                    # 生成补货单
                    search_list = [('partner_id', '=', line_obj.partner_id.id), ('state', '=', 'draft')]
                    stock_pick_add = self.env['stock.pick.add'].search(search_list)
                    stock_pick_add = stock_pick_add and stock_pick_add[0]
                    if not stock_pick_add:
                        values = {
                            'name': "%sA%s" % (line_obj.partner_id.name, line_obj.id),
                            'origin': line_obj.partner_id.name,
                            'state': 'draft',
                            'partner_id': line_obj.partner_id.id,
                        }
                        stock_pick_add = self.env['stock.pick.add'].create(values)
                    # 判断补货单明细中是否存在该产品
                    search_list = [('add_id', '=', stock_pick_add.id), ('product_id', '=', line_obj.product_id.id)]
                    add_line = self.env['stock.pick.add.line'].search(search_list)
                    if add_line:
                        add_line.product_qty += exchange_qty
                    else:
                        stock_pick_add.write({
                            'add_lines': [(0, 0, {'product_id': line_obj.product_id.id, 'product_qty': exchange_qty})]
                        })
                line_obj.write(line_values)
            return 'success'
        return 'failed'


    @api.model
    def get_check_customer_info(self):
        """获得验货的客户信息"""
        res = {
            'code': 'failed',
            'currentCustomer': {},
            'currentOrder': {}
        }
        order = self.env['out.picking.quality'].search([('user_id', '=', self.env.uid)])
        if not order:
            order = self.env['out.picking.quality'].create({'user_id': self.env.uid})
        else:
            if order.order_id:
                res['currentOrder'] = {
                    'id': order.order_id.id,
                    'name': order.order_id.name
                }
            if order.current_customer:
                res['currentCustomer']['id'] = order.current_customer.id
                res['currentCustomer']['name'] = order.current_customer.name or ""
                res['currentCustomer']['phone'] = order.current_customer.phone or ""
            last_customer = []
            for line in order.last_customer:
                last_customer.append({
                    'id': line.customer.id,
                    'name': line.customer.name or "",
                    'phone': line.customer.phone or "",
                })
            res['lastCustomerList'] = last_customer
            res['code'] = 'success'
        return res

    @api.model
    def get_wait_check_order(self):
        """获得待验货的出库"""
        res = {
            'code': 'failed',
            'data': []
        }
        out_quality_orders = self.env['out.quality.order'].search([('state', '!=', 'done')],order='partner_id, id desc')
        data_list = []
        for line in out_quality_orders:
            data_list.append({
                'id': line.id,
                'name': line.name,
                "pick_user": (line.pick_user and line.pick_user.name) or "",
                'customer': (line.partner_id and line.partner_id.name) or ""
            })
        if data_list:
            res['code'] = 'success'
            res['data'] = data_list
        return res
    @api.model
    def get_all_check_order_line(self):
        """获得当前质检订单所有的明细"""
        res = {
            'code': 'failed',
            'data': [],
            'message': "",
        }
        out_picking_quality = self.env['out.picking.quality'].search([('user_id', '=', self.env.uid)])

        if out_picking_quality and out_picking_quality.order_id:
            lines = out_picking_quality.order_id.line_ids
            line_list = []
            for line in lines:
                line_list.append({
                    'id': line.id,
                    'name': line.name,
                    'partner': line.partner_id.name,
                    'product': line.product_id.name,
                    'product_code': line.product_code,
                    'weight': line.weight,
                    'net_weight': line.net_weight,
                    'check_weight': line.check_weight,
                    'exchange_qty': line.exchange_qty,
                    'back_qty': line.back_qty,
                    'qty': line.qty,
                    'back_weight': line.back_weight,
                    'state': self._order_line_state.get(line.state, u"状态未知"),
                })
            res['data'] = line_list
            res['code'] = 'success'

        else:
            res['message]'] = "当前用户没有在质检的订单"
        return res

    @api.model
    def add_customer_order_check(self, order_id=""):
        '''添加订单为待捡订单'''
        if not order_id:
            return 'failed'
        out_picking_quality_obj = self.env['out.picking.quality']
        out_quality_order = self.env['out.quality.order'].search([('id', '=', order_id)], limit=1)
        if out_quality_order:
            out_picking_quality = out_picking_quality_obj.search([('user_id', '=', self.env.uid)])
            if not out_picking_quality:
                out_picking_quality = out_picking_quality_obj.create({'user_id': self.env.uid})
            out_picking_quality.order_id = out_quality_order
            if out_picking_quality.current_customer != out_quality_order.partner_id:
                #切换
                last_customer = [(0, 0, {'customer': out_picking_quality.current_customer.id})]
                for line in out_picking_quality.last_customer:
                    if line.customer.id == out_quality_order.partner_id.id:
                        line.unlink()
                out_picking_quality.write({
                    'current_customer': out_quality_order.partner_id.id,
                    'last_customer': last_customer,
                    'order_id': out_quality_order.id,
                })
            return 'success'
        return 'failed'
    @api.model
    def get_one_check_package(self, package_num=""):
        res = {
            'code': 'failed',
            'data': {},
            'message': "",
        }
        out_picking_quality = self.env['out.picking.quality'].search([('user_id', '=', self.env.uid)])

        if out_picking_quality:
            order_id = out_picking_quality.order_id.id
            package = self.env['out.quality.order.line'].search([('quality_order_id', '=', order_id), ('name', '=', package_num)])
            if package:
                values = {
                    'id': package.id,
                    'name': package.name,
                    'partner': package.partner_id.name,
                    'product': package.product_id.name,
                    'product_code': package.product_code,
                    'weight': package.weight,
                    'net_weight': package.net_weight,
                    'check_weight': package.check_weight,
                    'exchange_qty': package.exchange_qty,
                    'back_qty': package.back_qty,
                    'qty': package.qty,
                    'back_weight': package.back_weight,
                }
                res['data'] = values
                res['code'] = 'success'
            else:
                res['message'] = u"质检包号不存在,或者质检包不为当前质检订单:"+ out_picking_quality.order_id.name
        else:
            res['message'] = u"质检单号不存在"

        return res

class last_check_customer(models.Model):
    _name = 'last.check.customer'
    _order = 'id desc'
    record_id = fields.Many2one('out.picking.quality', ondelete='cascade', string='users')
    customer = fields.Many2one('res.partner', string='recent customer')
