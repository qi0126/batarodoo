# -*- coding: utf8 -*-
from openerp import api, fields, models
import time
import re
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class CustomerOder(models.Model):
    _name = 'batar.customer.sale'
    _order = 'id desc'

    name = fields.Char(string='Name')
    # out_ids = fields.One2many('stock.picking', 'customer_sale_id', string='Out Order')
    partner_id = fields.Many2one('res.partner', string='Customer')
    line_ids = fields.One2many('customer.sale.line', 'line_id', string='Lines')
    state = fields.Selection([('draft', 'Draft'), ('process', 'Process'),('warning','warning'), ('done', 'Done')], string='State')
    material_price_line = fields.One2many('zhanting.material.price','order_id',string='customer material price')
    total_weight = fields.Float(string='total weight',compute="_get_total_info")
    total_money = fields.Float(string='total money',compute="_get_total_info")




    @api.model
    def check_order(self):
        '''处理当天的未完成订单信息'''
        orders = self.env['batar.customer.sale'].search([('state', '=', 'process')])
        if orders:
            orders.write({'state':'warning'})


    @api.model
    def _get_total_info(self):
        ''''''
        if self.line_ids:
            materail_price_dict= {}
            total_money = 0
            total_weight = 0
            for line in self.material_price_line:
                materail_price_dict[line.attribute_value_id.id] = line.price_unit
            for line in self.line_ids:
                weight = (line.order_qty+line.change_qty)*line.standard_weight
                total_weight += weight
                total_money += line.item_fee*(line.order_qty+line.change_qty) +(line.additional_fee+line.weight_fee)*weight
            self.total_money = total_money
            self.total_weight = total_weight

    @api.multi
    def action_confirm_done(self):

        self.write({'state':'done'})

    @api.model
    def get_customer_material_price(self,partner_id=None):

        material_price_line = []
        if partner_id:
            price_discount = 0
            attribute_id = \
                self.env['ir.model.data'].get_object_reference('product_info_extend', 'product_attribute_material')[1]
            attribute_values = self.env['product.attribute.value'].search([('attribute_id', '=', attribute_id)])
            for attribute_value in attribute_values:
                # 搜索是否针对客户设置了材质价格
                customer_ornament_price_obj = self.env['customer.ornament.price'].search(
                    [('partner_id', '=', partner_id), ('attribute_value_id', '=', attribute_value.id),
                     ('active', '=', True)])
                price_unit = 0
                # 若存在为客户单独设置的材质价格
                if customer_ornament_price_obj:
                    price_unit = customer_ornament_price_obj.material_price + customer_ornament_price_obj.ornament_price
                    price_discount = customer_ornament_price_obj.sys_ornament_price - customer_ornament_price_obj.ornament_price
                    if price_discount < 0:
                        price_discount = 0
                # 若没有设置材质价格，采用系统当前的材质价格作为默认的价格
                else:
                    price_unit = self.env['product.attribute.material.price'].search(
                        [('active', '=', True), ('attribute_value_id', '=', attribute_value.id)]).price_unit
                values = {

                    'attribute_value_id': attribute_value.id,
                    'price_unit': price_unit,
                    'price_discount': price_discount
                }
                material_price_line.append((0, 0, values))
        return material_price_line


class OderLine(models.Model):
    _name = 'customer.sale.line'

    def _get_material_value_id(self):
        '''返回产品的材质'''
        # 获得价格，工费等信息，
        material_price_lines = self.line_id.material_price_line
        material_price_dict = {}
        material_value_id = None
        for line in material_price_lines:
            material_price_dict[line.attribute_value_id.id] = line.price_unit
        attribute_value_ids = self.product_id.attribute_value_ids
        value_ids = material_price_dict.keys()
        for attribute_value_id in attribute_value_ids:
            value_id = attribute_value_id.id
            if value_id in value_ids:
                material_value_id = value_id
        return [material_value_id, material_price_dict]

    @api.one
    @api.depends('product_id')
    def _real_time_price_unit(self):
        ''''''
        if self.product_id:
            material_value_id, price_dict = self._get_material_value_id()
            if material_value_id and price_dict:
                self.real_time_price_unit = price_dict[material_value_id]
        else:
            self.real_time_price_unit = self.product_id.real_time_price_unit

    real_time_price_unit = fields.Float(compute='_real_time_price_unit', string='real time price unit')
    standard_weight = fields.Float(string="Standard Weight",compute="_product_fee", store=True)
    all_weights = fields.Float(string='all line weight')
    item_fee = fields.Float(string="Item Fee", compute="_product_fee", store=True)
    additional_fee = fields.Float(string='additional fee', compute="_product_fee", store=True)
    weight_fee = fields.Float(string="weight fee", compute="_product_fee", store=True)

    pick_ids = fields.Many2many('stock.picking', 'customer_sale_pick', 'sale_line_id','picking_id', string='Pick Order')
    pack_ids = fields.Many2many('stock.picking', 'customer_sale_pack', 'sale_line_id', 'picking_id', string='Pack Order')
    out_ids = fields.Many2many('stock.picking', 'customer_sale_out', 'sale_line_id', 'picking_id', string='Out Order')
    line_id = fields.Many2one('batar.customer.sale', string='Order')
    product_id = fields.Many2one('product.product', string='Product')
    order_qty = fields.Integer(compute="compute_state",string='Order qty')
    change_qty = fields.Integer(string='Change Qty')
    exchange_qty = fields.Integer(string='product exchange qty')
    state = fields.Selection(compute="compute_state",selection=[('pick', 'Picking'), ('pack', 'Packing'), ('out', 'Pay'), ('delivery', 'Delivery'),('done','Done')], string='State')
    change_state = fields.Boolean(string='change state',default=False,compute="_change_state")
    display = fields.Boolean(string='display',default=True)

    @api.model
    def _change_state(self):
        if self.change_qty!=0 or self.exchange_qty!=0:
            self.change_state = True
        else:
            self.change_state = False
    @api.one
    @api.depends('product_id', 'line_id.partner_id')
    def _product_fee(self):
        if self.product_id:
            self.standard_weight = self.product_id.standard_weight
            material_value_id = self._get_material_value_id()[0]
            # 当前时间，用于判断订单明细创建时间是否符合优惠时效
            now_date_time_stamp = int(time.time())
            # 获得工费信息
            # 如果对客户的具体产品进行设置
            # 搜索条件：优惠有效，具体的产品
            product_discount_first = self.env['product.discount'].search(
                [('partner_id', '=', self.line_id.partner_id.id), ('product_id', '=', self.product_id.id),
                 ('active', '=', True)])
            product_discount_second = self.env['product.discount'].search(
                [('partner_id', '=', self.line_id.partner_id.id), ('attribute_value_id', '=', material_value_id),
                 ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id), ('active', '=', True)])
            product_discount_third = self.env['product.discount'].search(
                [('partner_id', '=', self.line_id.partner_id.id), ('categ_id', '=', self.product_id.categ_id.id),
                 ('active', '=', True)])
            product_discount_fourth = self.env['product.discount'].search(
                [('partner_id', '=', self.line_id.partner_id.id), ('applied_on', '=', '3_global'),
                 ('active', '=', True)])

            # 如果有标准重量，写入标准重量
            attribute_value_ids = self.product_id.attribute_value_ids

            for attribute_value_id in attribute_value_ids:
                if attribute_value_id.attribute_id.code == "weight":
                    m = re.match(r"(^[0-9]\d*\.\d|\d+)", attribute_value_id.name)
                    if m:
                        standard_weight = m.group(1)
                        self.standard_weight = float(standard_weight)

            # 如果有产品系列优惠
            if product_discount_first:
                if self._time_vaild(now_date_time_stamp, product_discount_first):
                    # 优惠在时效内,并且最小购买数量符合要求
                    self._get_fee(product_discount_first)
            # 如果存在产品模版优惠
            elif product_discount_second:
                if self._time_vaild(now_date_time_stamp, product_discount_second):
                    # 优惠在时效内,并且最小购买数量符合要求
                    self._get_fee(product_discount_second)
            # 如果存在产品类别优惠
            elif product_discount_third:
                if self._time_vaild(now_date_time_stamp, product_discount_third):
                    # 优惠在时效内,并且最小购买数量符合要求
                    self._get_fee(product_discount_third)
            # 如果存在所有产品优惠
            elif product_discount_fourth:
                if self._time_vaild(now_date_time_stamp, product_discount_fourth):
                    # 优惠在时效内,并且最小购买数量符合要求
                    self._get_fee(product_discount_fourth)
            # 如果优惠不存在，使用产品默认的费用
            else:
                self.additional_fee = self.product_id.additional_fee
                self.weight_fee = self.product_id.weight_fee
                self.item_fee = self.product_id.item_fee


    def _time_vaild(self, time_stamp=int(time.time()), product_discount_obj=None):
        '''判断时间是否有效'''
        if product_discount_obj is None:
            return False
        flag = True
        date_start = product_discount_obj.date_start
        date_end = product_discount_obj.date_end
        # 判断时间是否有效，若优惠没有设置时间期限，则一直有效
        if date_start:
            date_start_time_stamp = int(time.mktime(time.strptime(date_start, DATE_FORMAT)))
            # 当前时间在优惠开始日期之前
            if time_stamp < date_start_time_stamp:
                flag = False
        if date_end:
            date_end_time_stamp = int(time.mktime(time.strptime(date_end, DATE_FORMAT)))
            # 当前时间在优惠结束日期之后
            if time_stamp > date_end_time_stamp:
                flag = False
        return flag

    # @api.model
    @api.multi
    @api.depends('pick_ids', 'pack_ids', 'out_ids')
    def compute_state(self):
        '''计算状态'''

        for order_line in self:
            pick_ids_state = [str(line.state) for line in order_line.pick_ids if line.state !='cancel']
            pick_ids_state = list(set(pick_ids_state))
            pack_ids_state = [str(line.state) for line in order_line.pack_ids if line.state !='cancel']
            pack_ids_state = list(set(pack_ids_state))
            out_ids_state = [str(line.state) for line in order_line.out_ids if line.state !='cancel']
            #计算去掉cancel状态中的数量，（ 由于stock_picking中无法判断出cancel状态)
            assigned_picks = [line.id for line in order_line.pick_ids if line.state =='assigned']
            assigned_packs = [line.id for line in order_line.pack_ids if line.state == 'assigned']
            done_outs = [line.id for line in order_line.out_ids if line.state == 'done' ]
            assigned_outs = [line.id for line in order_line.out_ids if line.state == 'assigned' or line.state == 'partially_avaiable' ]
            # assigned_outs = [line.id for line in order_line.out_ids if line.state == 'assigned' or line.state == 'partially_avaiable' or line.state == 'done']

            qty = 0

            pick_ops = self.env['stock.pack.operation'].search([('picking_id','in',assigned_picks),('product_id','=',order_line.product_id.id)])
            for pick_op in pick_ops:
                qty += pick_op.product_qty-pick_op.qty_return

            pack_ops = self.env['stock.pack.operation'].search(
                [('picking_id', 'in', assigned_packs), ('product_id', '=', order_line.product_id.id)])
            for pack_op in pack_ops:
                qty += pack_op.product_qty - pack_op.qty_return

            assigned_out_ops = self.env['stock.pack.operation'].search(
                [('picking_id', 'in', assigned_outs), ('product_id', '=', order_line.product_id.id)])
            for assigned_out_op in assigned_out_ops:
                qty += assigned_out_op.product_qty- assigned_out_op.qty_return

            out_ops = self.env['stock.pack.operation'].search(
                [('picking_id', 'in', done_outs), ('product_id', '=', order_line.product_id.id)])
            for out_op in out_ops:
                qty += out_op.product_qty

            order_line.order_qty = qty

            # if order_line.order_qty == 0:
            #     # order_line.unlink()
            #     continue
            out_ids_done = [line.is_delivery for line in order_line.out_ids if line.state != 'cancel']
            out_ids_done = list(set(out_ids_done))
            out_ids_state = list(set(out_ids_state))
            if pick_ids_state != ['done']:
                order_line.state = 'pick'
                continue
            elif pack_ids_state != ['done']:
                order_line.state = 'pack'
                continue
            elif out_ids_state != ['done']:
                order_line.state = 'out'
                continue
            elif out_ids_done == [True]:
                order_line.state = 'done'
                continue
            else:
                order_line.state = 'delivery'


