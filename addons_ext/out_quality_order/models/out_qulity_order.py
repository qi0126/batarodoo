# -*- coding: utf-8 -*-

from openerp import models, fields, api


class stock_weigh(models.Model):
    _inherit = "stock.weigh"

    @api.model
    def pick_weigh_done(self, lineId="", netWeight=0, grossWeight=0):
        """写入分拣包重量信息"""
        res = super(stock_weigh, self).pick_weigh_done(lineId, netWeight, grossWeight)
        batar_package_obj = self.env['batar.package']
        batar_package = batar_package_obj.search([('id', '=', lineId)])
        if batar_package:
            mobile_picking = batar_package.mobile_picking
            states = [str(line.state) for line in mobile_picking.package_ids]
            states = list(set(states))
            # 若所有的都完成，创建客户验货单,如果客户的订单没有开始验货，合并验货单
            if states == ['done']:
                out_quality_order_obj = self.env['out.quality.order']
                out_quality_order_line = self.env['out.quality.order.line']
                line_values = []
                package_ids = mobile_picking.package_ids
                out_quality_order = out_quality_order_obj.search(
                    [('partner_id', '=', mobile_picking.partner_id.id), ('state', '=', 'draft')])
                for package in package_ids:
                    line_value = {
                        'name': package.name,
                        'partner_id': package.partner_id.id,
                        'product_id': package.product_id.id,
                        'product_code': package.product_code,
                        'net_weight': package.net_weight,
                        'weight': package.weight,
                        'check_weight': package.net_weight,
                        'qty': package.qty,
                        'ref': package.ref,
                        'state': 'draft',
                    }
                    if out_quality_order:
                        line_value['quality_order_id'] = out_quality_order.id
                        out_quality_order_line.create(line_value)
                    line_values.append((0,0,line_value))
                if not out_quality_order:
                    values = {
                        'partner_id':mobile_picking.partner_id.id,
                        'pick_user':mobile_picking.user_id.id,
                        'name':mobile_picking.name,
                        'line_ids':line_values,
                        'state': 'draft',
                    }

                    out_quality_order_obj.create(values)
        return res


class out_quality_order(models.Model):
    _name = 'out.quality.order'

    _STATE = [
        ('draft', 'wait confirm check'),
        ('wait', 'wait customer check'),
        ('ok', 'check ok'),
        ('has_back_or_exchange', 'some product need back or exchange'),
        ('done', 'check done')
    ]
    state = fields.Selection(_STATE, string='check state')
    name = fields.Char(string='out quliaty order name')
    pick_user = fields.Many2one('res.users', string='picking man')
    partner_id = fields.Many2one("res.partner", string='customer')
    line_ids = fields.One2many('out.quality.order.line', 'quality_order_id', string="out quality order line")
    back_lines = fields.One2many("out.quality.order.line.back","quality_order",string="out quality order back line")
    exchange_lines = fields.One2many("out.quality.order.line.exchange", "quality_order", string="out quality order exchange line")


    @api.multi
    def gen_back_order(self):
        """生成退货单"""
        for order in self:
            partner = order.partner_id
            back_lines = order.back_lines
            for back_line in back_lines:
                if back_line.generated:
                    continue
                search_list = [('name','=',back_line.order_line.name)]
                batar_package = self.env['batar.package'].search(search_list)
                batar_package = batar_package and batar_package[0]
                if batar_package:
                    mobile_picking = batar_package.mobile_picking
                    pick_ids = mobile_picking.pick_ids
                    group_ids = [line.group_id.id for line in pick_ids]
                    out_type_id = self.env['stock.picking.type'].with_context(lang='en').search(
                        [('name', 'ilike', 'Delivery Orders')], limit=1).id
                    out_ids = self.env['stock.picking'].search([('picking_type_id','=',out_type_id),('group_id','in',group_ids)])

                    search_list = [('picking_id', 'in', [line.id for line in out_ids]),
                                       ('product_id', '=', back_line.product_id.id),
                                       ('picking_id.state', '!=', 'done')]
                    stock_operations = self.env['stock.pack.operation'].search(search_list)
                    back_qty = back_line.qty
                    for stock_operation in stock_operations:
                        can_return_qty = int(stock_operation.product_qty - stock_operation.qty_return)
                        if back_qty > can_return_qty:
                            stock_operation.qty_return += can_return_qty

                            back_qty -= can_return_qty
                            stock_operation.qty_done = stock_operation.product_qty - stock_operation.qty_return
                        else:
                            stock_operation.qty_return += back_qty
                            stock_operation.qty_done = stock_operation.product_qty - stock_operation.qty_return
                            back_qty = 0
                            break
                    if back_qty == 0:
                        back_line.generated = True

class out_quality_order_line(models.Model):
    _name = 'out.quality.order.line'

    _STATE = [
        ('draft', 'wait confirm check'),
        ('wait', 'wait customer check'),
        ('ok', 'check ok'),
        ('has_back_or_exchange', 'some product need back or exchange'),
        ('done', 'check done')
    ]
    name = fields.Char(string='Name', default='/')
    partner_id = fields.Many2one('res.partner', string='Partner')
    product_id = fields.Many2one('product.product', string='Product')
    product_code = fields.Char(string='Product Code')
    weight = fields.Float(string="Weight")
    net_weight = fields.Float(string='Net Weight')
    check_weight = fields.Float(string="Check Weight")
    qty = fields.Float(string='Qty')
    exchange_qty = fields.Float(string="exchange qty", default=0)
    back_qty = fields.Float(string="back qty", default=0)
    ref = fields.Char(string='Ref Panwei')
    check_user_id = fields.Many2one('res.users', string='check user who check product with customer')
    state = fields.Selection(_STATE,string='check state')
    quality_order_id = fields.Many2one('out.quality.order', string="out quality order")
    back_lines = fields.One2many("out.quality.order.line.back","order_line",string="out quality order back line")
    back_weight = fields.Float(string="back weight")
    exchange_lines = fields.One2many("out.quality.order.line.exchange","order_line",string="out quality order back line")



class out_quality_order_line_back(models.Model):
    """退货和换货的数据"""
    _name = 'out.quality.order.line.back'
    order_line = fields.Many2one("out.quality.order.line", string="out quality order line")
    quality_order = fields.Many2one("out.quality.order", string='out quality order')
    product_id = fields.Many2one("product.product", string="Product")
    qty = fields.Float(string='Qty')
    net_weight = fields.Float(string="Net Weight")
    check_user_id = fields.Many2one("res.users", string='check user who check product with customer')
    generated = fields.Boolean(default=False,string="has generated order")


class out_quality_order_line_exchange(models.Model):
    """退货和换货的数据"""
    _name = 'out.quality.order.line.exchange'
    order_line = fields.Many2one("out.quality.order.line", string="out quality order line")
    quality_order = fields.Many2one("out.quality.order", string='out quality order')
    product_id = fields.Many2one("product.product", string="Product")
    qty = fields.Float(string='Qty')
    check_user_id = fields.Many2one("res.users", string='check user who check product with customer')
    generated = fields.Boolean(default=True,string="has generated order")




