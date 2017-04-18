# -*- coding: utf-8 -*-


from openerp import api, models, fields
import re
import pytz

from datetime import datetime, timedelta
from openerp.exceptions import UserError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF


class zhanting(models.Model):
    _name = 'zhanting'

    CustomerOrderState = {
        'pick': u'分拣中',
        'pack': u'待验',
        'out': u'待付款',
        'delivery': u'待发货',
        'done':u"已发货",
    }
    @api.model
    def get_current_customer(self, user=None):
        '''获得当前用户的当前客户信息'''
        current_customer = {}
        if user and user.current_customer:
            current_customer['id'] = "currentCustomer-%s" % user.current_customer.id
            current_customer['name'] = user.current_customer.name or ""
            current_customer['phone'] = user.current_customer.mobile or ""
            current_customer['code'] = user.current_customer.customer_code or ""
        return current_customer

    @api.model
    def get_recent_customer(self, user=None):
        '''获得当前用户的最近客户信息'''
        recent_customer_list = []
        if user and user.recent_customer:
            recent_customer = user.recent_customer

            for line in recent_customer:
                if line.customer:
                    customer_dict = {}
                    customer_dict['id'] = "recentCustomer-%s" % line.customer.id
                    customer_dict['name'] = line.customer.name or ""
                    customer_dict['phone'] = line.customer.mobile or ""
                    customer_dict['code'] = line.customer.customer_code or ""

                    recent_customer_list.append(customer_dict)
        return recent_customer_list

    @api.model
    def get_products_by_code(self, default_code="", offset=0, limit=20):
        '''根据产品编码进行搜索'''

        # default_code = str(default_code)

        tab_location_products = []
        user = self.env['res.users'].search([('id', '=', self._context['uid'])])
        if not default_code:
            return self.get_product_sample_location(user, 0, 20)
        # 获得所有的样品库信息
        sample_locations = self.env['stock.location'].search([('is_sample', '=', True)])
        for sample_location in sample_locations:
            tab_location = self.get_one_page_tab_location(offset, limit, sample_location.id, None, default_code, has_stock=False)
            if tab_location:
                tab_location_products.append(tab_location)
        if tab_location_products:
            tab_location_products[0]['tab_location_class'] = "tab-pane fade in active"

        return tab_location_products
    @api.model
    def get_draft_order_total(self,):
        '''获得某个客户在某个业务员下的所有订单汇总数据'''
        user = self.env['res.users'].search([('id', '=', self._context['uid'])])
        res = {
            'totalWeight':0,
            'totalMoney':0,
        }
        curstomer_id = user.current_customer and user.current_customer.id
        if curstomer_id:
            dt = fields.Datetime.to_string(datetime.utcnow() - timedelta(seconds=60*60*24))
            search_list = [ ('state', '=', 'draft'), ('user_id', '=', user.id), ('partner_id', '=', curstomer_id),('create_date', '>', dt)]
            orders = self.env['sale.order'].search(search_list)
            for order in orders:
                res['totalWeight'] += order.total_weight
                res['totalMoney'] += order.amount_total

        res['totalWeight'] = round(res['totalWeight'],2)
        res['totalMoney'] = round(res['totalMoney'],2)
        return res

    @api.model
    def search_customer_dict(self, offset=0, limit=20, customerInfo=""):
        if not  customerInfo:
            return self.get_today_customers(offset, limit)
        customer_info_dict = {}
        customer_list = []

        search_list = ['|', '|', ('name', 'like', customerInfo), ('customer_code', 'like', customerInfo),
                       ('mobile', 'like', customerInfo), ('is_company', '=', True), ('customer', '=', True)]
        page_count = self.env['res.partner'].search_count(search_list)
        if page_count % limit:
            all_page = int(page_count / limit) + 1
        else:
            all_page = int(page_count / limit)
        page_list = [i + 1 for i in range(all_page)]
        page_num = len(page_list)
        if page_num == 1:
            page_list = []
        elif page_num > 5:
            customer_info_dict['page_last'] = page_num
            if offset - 2 < 0:
                page_list = page_list[0:5]
            elif offset + 2 >= page_num:
                page_list = page_list[page_num - 5:page_num]
            else:
                page_list = page_list[offset - 2:offset + 3]
        else:
            pass
        customers = self.env['res.partner'].search(search_list, offset=offset * limit, limit=limit)
        for customer in customers:
            customer_list.append({
                'id':customer.id,
                'name': customer.name or "",
                'customer_code': customer.customer_code or "",
                'phone': customer.mobile or "",
                'order_time': u"系统无客户今日单"
            })
        customer_info_dict['customer_list'] = customer_list
        customer_info_dict['page_list'] = page_list
        customer_info_dict['current_page'] = offset + 1


        return  customer_info_dict

    @api.model
    def get_today_customers(self, offset=0, limit=20):
        '''获得今日所有的客户'''
        customer_info_dict = {}
        customer_list = []

        now = datetime.now(pytz.timezone('UTC'))
        start_time = datetime(now.year, now.month, now.day, 0, 0, 0)
        start_time_str = start_time.strftime(DF)
        query_results = """SELECT partner_id from sale_order  WHERE  create_date > %s  GROUP BY partner_id ; """

        self.env.cr.execute(query_results, (start_time_str,))
        query_results = self.env.cr.dictfetchall()
        customer_ids = [line['partner_id'] for line in query_results]
        customer_ids = list(set(customer_ids))
        page_count = len(customer_ids)
        all_page = 0
        if page_count % limit:
            all_page = int(page_count / limit) + 1
        else:
            all_page = int(page_count / limit)
        page_list = [i + 1 for i in range(all_page)]
        page_num = len(page_list)
        if page_num == 1:
            page_list = []
        elif page_num > 5:
            customer_info_dict['page_last'] = page_num
            if offset - 2 < 0:
                page_list = page_list[0:5]
            elif offset + 2 >= page_num:
                page_list = page_list[page_num - 5:page_num]
            else:
                page_list = page_list[offset - 2:offset + 3]
        else:
            pass
        # customer_ids = customer_ids[offset*limit:(offset+1)*limit]

        customer_dict = {}

        for partner_id in customer_ids:

            order = self.env['sale.order'].search([('partner_id', '=', partner_id)], order='id desc', limit=1)
            create_date = datetime.strptime(order.create_date, DF)
            create_date = create_date + timedelta(seconds=8 * 60 * 60)
            create_date = create_date.strftime(DF)
            customer_dict[order.id] = {
                'id': order.partner_id.id,
                'name': order.partner_id.name or "",
                'customer_code': order.partner_id.customer_code or "",
                'phone': order.partner_id.mobile or "",
                'order_time': create_date
            }


        sort_by = customer_dict.keys()
        sort_by.sort(reverse=True)
        sort_by = sort_by[offset * limit:(offset + 1) * limit]
        for key in sort_by:
            customer_list.append(customer_dict[key])
        customer_info_dict['customer_list'] = customer_list
        customer_info_dict['page_list'] = page_list
        customer_info_dict['current_page'] = offset + 1


        return customer_info_dict

    @api.model
    def current_customer_product_dict(self, customer_id=None, location_id=None):
        '''获得客户某个柜台的草稿订单产品数据'''
        current_customer_product_dict = {}
        if not customer_id or  (not location_id):
            return current_customer_product_dict
        if customer_id:
            order = self.env['sale.order'].search(
                [ ('user_id', '=', self._context['uid']), ('partner_id', '=', customer_id),
                 ('state', '=', 'draft'), ('product_sample_location', '=', location_id)])
            if order:
                for order_line in order.order_line:
                    product_order_key = "%s" % order_line.product_id.id
                    current_customer_product_dict[product_order_key] = int(order_line.product_uom_qty or 0)
        return current_customer_product_dict

    @api.model
    def gen_tab_location_product_info(self, products=[], current_customer_product_dict={}):
        '''生成tab页的产品信息'''
        product_list_info = []
        for product in products:

            info = {}
            key = "%s" % product.id

            info['id'] = key
            info['default_code'] = product.default_code
            info['virtual_available'] = product.virtual_available
            name = product.name_get()[0][1]
            if product.description_sale:
                name += '\n' + product.description_sale
            info['name'] = name
            info['uom_id'] = product.uom_id.id
            info['item_fee'] = product.item_fee or 0
            info['product_material'] = product.material
            info['real_time_price_unit'] = product.real_time_price_unit or 0
            info['additional_fee'] = product.additional_fee or 0
            info['weight_fee'] = product.weight_fee or 0
            info['standard_weight'] = 0


            info['order_qty'] = current_customer_product_dict.get(key, 0)

            attribute_value_ids = product.attribute_value_ids
            for attribute_value_id in attribute_value_ids:
                if attribute_value_id.attribute_id.code == "weight":
                    m = re.match(r"(^[0-9]\d*\.\d|\d+)", attribute_value_id.name)
                    if m:
                        standard_weight = m.group(1)
                        info['standard_weight'] = float(standard_weight)
            # if product.uom_id.name == "Unit(s)" or product.uom_id.name ==u"件":
            if product.uom_id.with_context(**{'lang': "en"}).name == "Unit(s)":
                info['unitClass'] = "numClass"
                info['step'] = 1
            else:
                info['unitClass'] = "weightClass"
                info['step'] = info['standard_weight']
                if info['virtual_available'] < info['standard_weight']:
                    info['virtual_available'] = 0
            product_list_info.append(info)
        return product_list_info
    @api.model
    def get_product_sample_location(self, user=None, offset=0, limit=20):
        '''获得当前用户的柜台客户信息'''
        tab_location_products = []
        if user and user.product_sample_location:

            locations = user.product_sample_location
            for line in locations:
                customer_id = user.current_customer and user.current_customer.id
                tab_location = self.get_one_page_tab_location(offset, limit, line.id, customer_id, has_stock=True)
                if tab_location:
                    tab_location_products.append(tab_location)

        return  tab_location_products

    @api.model
    def get_one_page_tab_location(self, offset=0, limit=20, location_id=None, customer_id=None, default_code='', has_stock=False):

        ''''''
        # default_code = str(default_code)
        location = self.env['stock.location'].search([('id', '=', location_id)])
        tab_location = {}
        if not location_id:
            return tab_location
        search_list = [('sale_ok', '=', True), ('active', '=', True), ('product_sample_location', '=', location.id)]
        if default_code:
            search_list.append(('default_code', 'like', default_code))
        else:
            if has_stock:
                search_list.append(('has_stock', '=', True))
        current_customer_product_dict = self.current_customer_product_dict(customer_id, location.id)
        all_count = self.env['product.product'].search_count(search_list)
        all_page = 0
        if all_count % limit:

            all_page = int(all_count / limit) + 1
        else:
            all_page = int(all_count / limit)
        page_list = [i + 1 for i in range(all_page)]
        page_num = len(page_list)
        if page_num == 1:
            page_list = []
        elif page_num > 5:
            tab_location['page_last'] = page_num
            if offset - 2 < 0:
                page_list = page_list[0:5]
            elif offset + 2 >= page_num:
                page_list = page_list[page_num - 5:page_num]
            else:
                page_list = page_list[offset - 2:offset + 3]
        else:
            pass

        products = self.env['product.product'].search(search_list, offset=offset * limit, limit=limit, order='has_stock desc')
        product_list_info = self.gen_tab_location_product_info(products, current_customer_product_dict)
        if product_list_info:
            tab_location['name'] = location.name or ""
            tab_location['products'] = product_list_info
            tab_location['page_list'] = page_list or []
            tab_location['current_page'] = offset + 1
            tab_location['location_id'] = "location-%s" % location.id
            tab_location['location_id_href'] = "#location-%s" % location.id
            tab_location['tab_location_class'] = "tab-pane fade"
        return tab_location

    @api.model
    def get_current_user_info(self, offset=0, limit=20):
        '''获得当前用户的当前客户，最近客户，柜台产品信息'''

        user = self.env['res.users'].search([('id', '=', self._context['uid'])])

        current_customer = self.get_current_customer(user)
        recent_customer_list = self.get_recent_customer(user)
        tab_location_products = self.get_product_sample_location(user, offset, limit)
        res = {
            'top_title':u"购物大厅",
        }
        if tab_location_products:
            tab_location_products[0]['tab_location_class'] = "tab-pane fade in active"
            res['tab_location_products'] = tab_location_products

        if current_customer:
            res['current_customer'] = current_customer
        if recent_customer_list:
            res['recent_customer_list'] = recent_customer_list
        return res

    @api.model
    def search_customer(self, customerInfo=""):
        res = []
        if customerInfo:
            search_list = ['|', '|', ('name', 'like', customerInfo), ('customer_code', 'like', customerInfo), ('mobile', 'like', customerInfo), ('is_company', '=', True), ('customer', '=', True)]
            customer_list = self.env['res.partner'].search(search_list)
            for line in customer_list:
                customer_dict = {}
                customer_dict['id'] = line.id
                customer_dict['name'] = line.name
                res.append(customer_dict)
        return res

    @api.model
    def change_current_customer(self, customer_info="", customer_id=None, limit=20):
        '''变更当前客户'''
        res = {}
        if not customer_id and not customer_info:
            res['code'] = 'failed'
            res['message'] = u"客户信息不存在"
            return res
        else:

            search_list = [('is_company', '=', True), ('customer', '=', True)]
            if customer_id:
                search_list.append(('id', '=', customer_id))


            elif customer_info:
                search_list.append(('name', '=', customer_info))

            customer = self.env['res.partner'].search(search_list)

            if not customer:
                res['code'] = 'failed'
                res['message'] = u"客户信息不存在"
                return res
            else:
                user = self.env['res.users'].search([('id', '=', self._context['uid'])])

                current_customer = user.current_customer and user.current_customer.id
                if current_customer != customer.id:
                    user.sudo().write({
                        'current_customer': customer.id,
                        'recent_customer': [(0, 0, {'customer': current_customer})],
                    })
                    if current_customer:
                        recent = self.env['recent.customer'].search(
                            [('user_id', '=', user.id), ('customer', '=', customer.id)])
                        if recent:
                            recent.unlink()
        res = self.get_current_user_info(0, limit)
        res['code'] = 'success'
        return res

    @api.model
    def create_sale_order(self, customer, product_sample_location):
        ''''''
        vals = {

            'product_sample_location':product_sample_location,
        }
        vals['partner_id'] = customer.id
        material_price_line = []
        price_discount = 0
        attribute_id = \
            self.env['ir.model.data'].get_object_reference('product_info_extend', 'product_attribute_material')[1]
        attribute_values = self.env['product.attribute.value'].search([('attribute_id', '=', attribute_id)])
        for attribute_value in attribute_values:
            # 搜索是否针对客户设置了材质价格
            customer_ornament_price_obj = self.env['customer.ornament.price'].search(
                [('partner_id', '=', customer.id), ('attribute_value_id', '=', attribute_value.id),
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
        vals['material_price_line'] = material_price_line
        order = self.env['sale.order'].create(vals)
        return order

    @api.model
    def merge_draft_order(self, order_list):

        order = order_list[0]
        length = len(order_list)
        for i in range(1, length):
            order_obj = order_list[i]

            order_lines = order_obj.order_line
            for line in order_lines:
                order_line = self.env['sale.order.line'].search([('order_id', '=', order.id), ('product_id', '=', line.product_id.id)])
                if order_line:
                    order_line.product_uom_qty += line.product_uom_qty
                else:
                    vals = {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                    }
                    attribute_value_ids = line.product_id.attribute_value_ids
                    for attribute_value_id in attribute_value_ids:
                        if attribute_value_id.attribute_id.code == "weight":
                            m = re.match(r"(^[0-9]\d*\.\d|\d+)", attribute_value_id.name)
                            if m:
                                standard_weight = m.group(1)
                                vals['standard_weight'] = float(standard_weight)
                                vals['all_weights'] = vals['standard_weight'] * line.product_uom_qty
                    order.write({
                        'order_line':[(0, 0, vals)]
                    })
            order_obj.unlink()

        return order


    @api.model
    def change_order_product_info(self, product_id=None, product_qty=0):
        '''
        修改订单中的产品信息，若客户不存在该柜台的草稿订单，则创建订单，添加产品，
        若数量为零，订单中存在该产品，则删除该产品

        '''

        product_qty = product_qty
        res = {
            'code':'failed',
            'message':u'信息不完整，请联系管理人员'
        }
        user = self.env['res.users'].search([('id', '=', self._context['uid'])])

        if not (user and product_id):
            return res
        else:
            customer_id = user.current_customer and user.current_customer.id
            if not customer_id:
                res['message'] = u'请先添加客户，再选产品'
                return  res
            product = self.env['product.product'].search([('id', '=', product_id)])

            if not product:
                res['message'] = u'产品添加错误，请联系管理人员'
                return res
            dt = fields.Datetime.to_string(datetime.utcnow() - timedelta(seconds=60*60*24))
            search_list = [('product_sample_location', '=', product.product_sample_location.id), \
                           ('user_id', '=', self._context['uid']), ('partner_id', '=', customer_id), ('state', '=', 'draft')]
                               # ('create_date', '>', dt)]
            order = self.env['sale.order'].search(search_list, order='id asc')
            if not order:
                order = self.create_sale_order(user.current_customer, product.product_sample_location.id)
            if len(order) > 1:
                order = self.merge_draft_order(order)
            vals = {
                'product_id': product_id,
                'product_uom_qty': product_qty,
            }
            res_standard_weight = 0
            attribute_value_ids = product.attribute_value_ids
            for attribute_value_id in attribute_value_ids:
                if attribute_value_id.attribute_id.code == "weight":
                    m = re.match(r"(^[0-9]\d*\.\d|\d+)", attribute_value_id.name)
                    if m:
                        standard_weight = m.group(1)
                        vals['standard_weight'] = float(standard_weight)
                        res_standard_weight =  vals['standard_weight']
                        vals['all_weights'] = vals['standard_weight'] * product_qty
            if not order:
                if product_qty > product.virtual_available:
                    product_qty = product.virtual_available
                    vals['product_uom_qty'] = product_qty
                order.write({
                    'order_line':[(0, 0, vals)]
                })
            else:
                order_line = self.env['sale.order.line'].search([('order_id', '=', order.id), ('product_id', '=', product.id)])

                max_product_qty = product.virtual_available + (0 or order_line.product_uom_qty)
                if product_qty > max_product_qty:
                    product_qty = max_product_qty
                    vals['product_uom_qty'] = product_qty
                if order_line:

                    if product_qty:
                        order_line.write(vals)
                    else:
                        order_line.unlink()
                else:
                    order.write({
                        'order_line': [(0, 0, vals)]
                    })
        res['code'] = 'success'
        res['message'] = u"添加成功"
        if product.uom_id.with_context(**{'lang': "en"}).name == "Unit(s)":
            res['unitClass'] = "numClass"


        else:
            res['unitClass'] = "weightClass"
        res['virtual_available'] = round(product.virtual_available,2)
        if res['virtual_available'] < res_standard_weight:
            res['virtual_available'] = 0
        res['product_qty'] = product_qty

        return res

    @api.model
    def get_one_page_tab_location_draft_order(self, offset=0, limit=20, location_id=None, default_code=''):
        ''''''
        # default_code = str(default_code)
        user = self.env['res.users'].search([('id', '=', self._context['uid'])])
        customer_id = user.current_customer and user.current_customer.id
        tab_location = {}
        if not customer_id:
            return tab_location
        search_list = [ ('state', '=', 'draft'), ('partner_id', '=', customer_id)]

        if location_id:
            search_list.append(('product_sample_location', '=', location_id))
        order = self.env['sale.order'].search(search_list, order='id asc')
        if len(order) > 1:
            order = self.merge_draft_order(order)
        if order:

            tab_location = {
                'name': order.product_sample_location.name,
                'products': [],
                'location_id': "location-%s" % order.product_sample_location.id,
                'location_id_href': "#location-%s" % order.product_sample_location.id,
                'tab_location_class': "tab-pane fade",
                'order_id': order.id,
            }
            product_list_info = []
            line_search_list = [('order_id', '=', order.id)]

            if default_code:
                line_search_list.append(('product_id.default_code', 'like', default_code))
            all_count = self.env['sale.order.line'].search_count(line_search_list)

            all_page = 0
            if all_count % limit:

                all_page = int(all_count / limit) + 1
            else:
                all_page = int(all_count / limit)
            page_list = [i + 1 for i in range(all_page)]
            page_num = len(page_list)
            if page_num == 1:
                page_list = []
            elif page_num > 5:
                tab_location['page_last'] = page_num
                if offset - 2 < 0:
                    page_list = page_list[0:5]
                elif offset + 2 >= page_num:
                    page_list = page_list[page_num - 5:page_num]
                else:
                    page_list = page_list[offset - 2:offset + 3]
            else:
                pass
            tab_location['page_list'] = page_list
            tab_location['current_page'] = offset + 1
            order_lines = self.env['sale.order.line'].search(line_search_list, offset=offset * limit, limit=limit, order='id desc')
            for line in order_lines:

                info = {}
                info['id'] = line.product_id.id
                info['default_code'] = line.product_id.default_code
                info['virtual_available'] = line.product_id.virtual_available
                name = line.product_id.name_get()[0][1]
                if line.product_id.description_sale:
                    name += '\n' + line.product_id.description_sale
                info['name'] = name
                info['uom_id'] = line.product_id.uom_id.id

                info['item_fee'] = line.item_fee or 0
                info['product_material'] = line.product_id.material
                info['real_time_price_unit'] = line.real_time_price_unit or 0
                info['additional_fee'] = line.additional_fee or 0
                info['weight_fee'] = line.weight_fee or 0
                info['standard_weight'] = line.standard_weight or 0
                info['order_qty'] = line.product_uom_qty
                # if line.product_id.uom_id.name == "Unit(s)" or line.product_id.uom_id.name  ==u"件":
                if line.product_id.uom_id.with_context(**{'lang': "en"}).name == "Unit(s)":
                    info['unitClass'] = "numClass"
                    info['step'] =1

                else:
                    info['unitClass'] = "weightClass"
                    info['step'] =  info['standard_weight']
                    if info['virtual_available'] < info['standard_weight']:
                        info['virtual_available'] = 0
                product_list_info.append(info)
            tab_location['products'] = product_list_info
            # 若没有数据则返回空
            if not product_list_info:
                tab_location = {}
        else:
            pass


        return tab_location

    @api.model
    def get_customer_confirm_order_info(self, offset=0, limit=20, location_id=None, default_code=''):
        # default_code = str(default_code)
        tab_location_products = []
        if location_id:
            tab_location = self.get_one_page_tab_location_confirm_order(offset, limit, location_id, default_code)
            if tab_location:
                tab_location_products.append(tab_location)
        else:
            sample_locations = self.env['stock.location'].search([('is_sample', '=', True)])
            for location in sample_locations:
                tab_location = self.get_one_page_tab_location_confirm_order(offset, limit, location.id, default_code)
                if tab_location:
                    tab_location_products.append(tab_location)
        if tab_location_products:
            tab_location_products[0]['tab_location_class'] = "tab-pane fade in active"
        return tab_location_products
    @api.model
    def get_customer_draft_order_info(self, offset=0, limit=20, location_id=None, default_code=''):
        '''获得客户的草稿订单信息'''
        # default_code = str(default_code)
        tab_location_products = []
        if location_id:
            tab_location = self.get_one_page_tab_location_draft_order(offset, limit, location_id, default_code)
            if tab_location:
                tab_location_products.append(tab_location)
        else:
            sample_locations = self.env['stock.location'].search([('is_sample', '=', True)])
            for location in sample_locations:
                tab_location = self.get_one_page_tab_location_draft_order(offset, limit, location.id, default_code)
                if tab_location:
                    tab_location_products.append(tab_location)
        if tab_location_products:
            tab_location_products[0]['tab_location_class'] = "tab-pane fade in active"
        return tab_location_products
    @api.model
    def get_confirm_total_info(self):
        result = {
            'total_weight':0,
            'total_money':0
        }
        user = self.env['res.users'].search([('id', '=', self._context['uid'])])
        customer_id = user.current_customer and user.current_customer.id
        if customer_id:
            order = self.env['batar.customer.sale'].search([('partner_id', '=', customer_id), ('state', '=', 'process')], limit=1, order='id desc')
            if order:
                result['total_weight'] = order.total_weight
                result['total_money'] = order.total_money

            if self.env['customer.sale.line'].search([('line_id', '=', order.id), ('change_qty', '!=', 0)]):
                result['show_total_button'] = 'inline'
            elif self.env['customer.sale.line'].search([('line_id', '=', order.id), ('exchange_qty', '!=', 0)]):
                result['show_total_button'] = 'inline'

        return result

    @api.model
    def get_total_buttons(self, customer_order=None, location_id=None):
        if not  customer_order  :
            return 'none'
        search_list = ["|", ('change_qty', '!=', 0), ('exchange_qty', '!=', 0), ('line_id', '=', customer_order.id), ('product_id.product_sample_location', '=', location_id), ('line_id.state', '=', 'process')]
        line = self.env['customer.sale.line'].search(search_list)
        if line:
            return "inline"
        return  'none'

    @api.model
    def get_one_page_tab_location_confirm_order(self, offset=0, limit=20, location_id=None, default_code=''):
        '''获得某一页确定的订单信息'''
        # default_code = str(default_code)
        # self.env['customer.sale.line'].search([('order_qty','=',0)]).unlink()
        user = self.env['res.users'].search([('id', '=', self._context['uid'])])
        customer_id = user.current_customer and user.current_customer.id
        tab_location = {}
        if not customer_id or not location_id:
            return tab_location
        location = self.env['stock.location'].search([('id', '=', location_id)])
        search_list = [('partner_id', '=', customer_id), ('state', '=', 'process')]
        customer_order = self.env['batar.customer.sale'].search(search_list)
        if not customer_order:
            return  tab_location
        all_lines = self.env['customer.sale.line'].search([('line_id', '=', customer_order.id)])
        for all_line in all_lines:
            if all_line.order_qty == 0 or all_line.state == 'done':
                all_line.display = False
            else:
                all_line.display = True


        line_search_list = [('line_id', '=', customer_order.id), ('display', '=', True)]
        if default_code:
            line_search_list.append(('product_id.default_code', 'like', default_code))
        if location_id:
            line_search_list.append(('product_id.product_sample_location', '=', location_id))
        all_count = self.env['customer.sale.line'].search_count(line_search_list)
        all_page = 0
        if all_count % limit:

            all_page = int(all_count / limit) + 1
        else:
            all_page = int(all_count / limit)
        page_list = [i + 1 for i in range(all_page)]
        page_num = len(page_list)
        if page_num == 1:
            page_list = []
        elif page_num > 5:
            tab_location['page_last'] = page_num
            if offset - 2 < 0:
                page_list = page_list[0:5]
            elif offset + 2 >= page_num:
                page_list = page_list[page_num - 5:page_num]
            else:
                page_list = page_list[offset - 2:offset + 3]
        else:
            pass
        tab_location['name'] = location.name or ""
        tab_location['page_list'] = page_list
        tab_location['current_page'] = offset + 1
        tab_location['location_id'] = "location-%s" % location.id
        tab_location['location_id_href'] = "#location-%s" % location.id
        tab_location['tab_location_class'] = "tab-pane fade"
        tab_location['change_num'] = 0
        product_list_info = []
        lines = self.env['customer.sale.line'].search(line_search_list, offset=offset * limit, limit=limit)
        for line in lines:
            if line.state == 'done':
                continue
            info = {}
            name = line.product_id.name_get()[0][1]
            if line.product_id.description_sale:
                name += '\n' + line.product_id.description_sale
            info['name'] = name
            info['id'] = line.product_id.id

            info['default_code'] = line.product_id.default_code
            info['order_qty'] = line.order_qty + line.change_qty
            info['total_qty'] = line.order_qty + line.change_qty
            info['state'] = self.CustomerOrderState.get(str(line.state), u"异常")
            info['virtual_available'] = line.product_id.virtual_available
            info['change_qty'] = line.change_qty
            info['exchange_qty'] = line.exchange_qty

            info['uom_id'] = line.product_id.uom_id.id
            info['item_fee'] = line.product_id.item_fee or 0
            info['product_material'] = line.product_id.material
            info['real_time_price_unit'] = line.product_id.real_time_price_unit or 0
            info['additional_fee'] = line.product_id.additional_fee or 0
            info['weight_fee'] = line.product_id.weight_fee or 0
            info['standard_weight'] = 0



            attribute_value_ids = line.product_id.attribute_value_ids
            for attribute_value_id in attribute_value_ids:
                if attribute_value_id.attribute_id.code == "weight":
                    m = re.match(r"(^[0-9]\d*\.\d|\d+)", attribute_value_id.name)
                    if m:
                        standard_weight = m.group(1)
                        info['standard_weight'] = float(standard_weight)
            # if line.product_id.uom_id.name == "Unit(s)" or product.uom_id.name ==u"件":
            if line.product_id.uom_id.with_context(**{'lang': "en"}).name == "Unit(s)":
                info['unitClass'] = "numClass"
                info['step'] = 1
            else:
                info['unitClass'] = "weightClass"
                info['step'] = info['standard_weight']
                if info['virtual_available'] < info['standard_weight']:
                    info['virtual_available'] = 0
            product_list_info.append(info)

        if not  product_list_info:
            tab_location = {}
        else:
            tab_location['products'] = product_list_info
        return  tab_location

    @api.model
    def get_confirm_order(self, offset=0, limit=20, location_id=None, default_code=''):
        '''获得确认的订单的信息'''
        # default_code = str(default_code)
        tab_location_products = []
        if location_id:
            tab_location = self.get_one_page_tab_location_confirm_order(offset, limit, location_id, default_code)
            if tab_location:
                tab_location_products.append(tab_location)
        else:
            sample_locations = self.env['stock.location'].search([('is_sample', '=', True)])
            for location in sample_locations:
                tab_location = self.get_one_page_tab_location_confirm_order(offset, limit, location.id, default_code)
                if tab_location:
                    tab_location_products.append(tab_location)
        if tab_location_products:
            tab_location_products[0]['tab_location_class'] = "tab-pane fade in active"
        return tab_location_products

    @api.model
    def change_confirm_order_product_info(self, product_id=None, product_qty=0, type=''):
        '''改变我的订单中产品的数量'''
        result = {
            'code':'failed',
        }

        user = self.env['res.users'].search([('id', '=', self._context['uid'])])
        customer_id = user.current_customer and user.current_customer.id
        order_line = None
        if not customer_id or not product_id:
             pass
        elif 'add' == type:
            order_line = self.env['customer.sale.line'].search([('line_id.partner_id', '=', customer_id), ('product_id', '=', product_id),
                 ('line_id.state', '=', 'process')])
            if order_line.product_id.virtual_available > order_line.change_qty:
                order_line.change_qty += product_qty
        elif 'sub' == type:
            order_line = self.env['customer.sale.line'].search([('line_id.partner_id', '=', customer_id), ('product_id', '=', product_id), ('line_id.state', '=', 'process')])
            if int(order_line.order_qty + order_line.change_qty) > 0:
                order_line.change_qty -= product_qty

        elif 'change' == type:
            order_line = self.env['customer.sale.line'].search(
                [('line_id.partner_id', '=', customer_id), ('product_id', '=', product_id),
                 ('line_id.state', '=', 'process')])
            max_qty = order_line.product_id.virtual_available + order_line.change_qty + order_line.order_qty
            product_qty = int(product_qty)
            if product_qty >= 0:
                if product_qty <= (max_qty):
                    order_line.change_qty = product_qty - order_line.order_qty
                else:
                    order_line.change_qty = max_qty - order_line.order_qty
            else:
                if abs(product_qty) >= (max_qty):
                    order_line.change_qty = -order_line.order_qty
                else:
                    order_line.change_qty = order_line.order_qty + product_qty
        else:
            pass
        if order_line:
            result['code'] = 'success'
            result['info'] = self.get_customer_line_info(order_line)
            if order_line.exchange_qty != 0 or order_line.change_qty != 0:
                result['cancel_current_button'] = 'inline'
        return result
    @api.model
    def get_customer_line_info(self, order_line=None):
        ''''''
        info = {}

        if not order_line:
            return info
        else:
            info = {}
            name = order_line.product_id.name_get()[0][1]
            if order_line.product_id.description_sale:
                name += '\n' + order_line.product_id.description_sale

            info['name'] = name
            info['id'] = order_line.product_id.id
            info['default_code'] = order_line.product_id.default_code
            info['order_qty'] = order_line.order_qty + order_line.change_qty
            info['total_qty'] = order_line.order_qty + order_line.change_qty
            info['state'] = self.CustomerOrderState.get(str(order_line.state), u"异常")
            info['virtual_available'] = order_line.product_id.virtual_available
            info['change_qty'] = order_line.change_qty
            info['exchange_qty'] = order_line.exchange_qty


            info['uom_id'] = order_line.product_id.uom_id.id
            info['item_fee'] = order_line.product_id.item_fee or 0
            info['product_material'] = order_line.product_id.material
            info['real_time_price_unit'] = order_line.product_id.real_time_price_unit or 0
            info['additional_fee'] = order_line.product_id.additional_fee or 0
            info['weight_fee'] = order_line.product_id.weight_fee or 0
            info['standard_weight'] = order_line.product_id.standard_weight or 0
            # if order_line.product_id.uom_id.name == "Unit(s)" or order_line.product_id.uom_id.name ==u"件":
            if order_line.product_id.uom_id.with_context(**{'lang': "en"}).name == "Unit(s)":
                info['unitClass'] = "numClass"
                info['step'] = 1
            else:
                info['unitClass'] = "weightClass"
                info['step'] = info['standard_weight']
                if info['virtual_available'] < info['standard_weight']:
                    info['virtual_available'] = 0
            return info
    @api.model
    def change_return_product_number(self, product_id=None, product_qty=0, type=''):
        '''退货数量改变'''
        result = {
            'code': 'failed',
        }

        product_qty = int(product_qty)
        user = self.env['res.users'].search([('id', '=', self._context['uid'])])
        customer_id = user.current_customer and user.current_customer.id
        order_line = None
        if not customer_id or not product_id:
            pass
        else:
            order_line = self.env['customer.sale.line'].search([('line_id.partner_id', '=', customer_id), ('product_id', '=', product_id), ('line_id.state', '=', 'process')])

            # max_exchange_qty = int(order_line.product_id.virtual_available)
            max_exchange_qty = order_line.order_qty
            if 'add' == type:
                if int(order_line.exchange_qty + product_qty) > max_exchange_qty:
                    # order_line.exchange_qty = max_exchange_qty
                    pass
                else:
                    order_line.exchange_qty += product_qty
            elif 'sub' == type:
                if int(order_line.exchange_qty) < product_qty:
                    pass
                    # order_line.exchange_qty = 0
                else:
                    order_line.exchange_qty -= product_qty
            elif 'change' == type:
                if product_qty < 0:
                    product_qty = 0
                if  product_qty > max_exchange_qty:
                    order_line.exchange_qty = max_exchange_qty
                else:
                    order_line.exchange_qty = product_qty
        if order_line:
            result['code'] = 'success'
            result['info'] = self.get_customer_line_info(order_line)
            if order_line.exchange_qty != 0 or order_line.change_qty != 0:
                result['cancel_current_button'] = 'inline'
        return result
    @api.model
    def cancel_all_change(self, offset=0, limit=20, location_id=None,):
        ''''''
        user = self.env['res.users'].search([('id', '=', self._context['uid'])])
        customer_id = user.current_customer and user.current_customer.id
        if customer_id:
            search_list = [('line_id.partner_id', '=', customer_id), ('line_id.state', '=', 'process'), ('product_id.product_sample_location', '=', location_id)]
            customer_sale_lines = self.env['customer.sale.line'].search(search_list)
            customer_sale_lines.write({
                'change_qty': 0,
                'exchange_qty': 0,
            })
        return self.get_one_page_tab_location_confirm_order(offset, limit, location_id, '')
    @api.model
    def cancel_current_page_change(self, offset=0, limit=20, location_id=None, product_ids=[]):
        ''''''
        user = self.env['res.users'].search([('id', '=', self._context['uid'])])
        customer_id = user.current_customer and user.current_customer.id
        if customer_id:
            search_list = [('line_id.partner_id', '=', customer_id), ('line_id.state', '=', 'process'), ('product_id', 'in', product_ids)]
            customer_sale_lines = self.env['customer.sale.line'].search(search_list)
            customer_sale_lines.write({
                'change_qty': 0,
                'exchange_qty': 0,
            })

        return self.get_one_page_tab_location_confirm_order(offset, limit, location_id, '')


    @api.model
    def create_stock_pick_add(self, customer, location_id='', customer_sale_line=None, batar_stock_pick_add=None, add_qty=0):
        '''补货'''
        if not batar_stock_pick_add:
            batar_stock_pick_add = self.env['stock.pick.add'].create({
                'name': "%sA%s" % (customer.name, customer_sale_line.id),
                'origin': customer.name,
                'state': 'draft',
                'partner_id': customer.id,
                'product_sample_location': location_id,
            })

        batar_stock_pick_add.write({
            'add_lines': [(0, 0, {'product_id': customer_sale_line.product_id.id, 'product_qty': add_qty})]
        })
        return  batar_stock_pick_add



    @api.model
    def confirm_change(self, location_id=None):
        '''确认当前柜台的变更'''
        if not location_id:
            raise UserError("无法确认更改")
        user = self.env['res.users'].search([('id', '=', self._context['uid'])])
        customer_id = user.current_customer and user.current_customer.id
        if not customer_id:
            raise UserError("无法确认更改")
        customer_name = user.current_customer.name

        search_list = [('line_id.partner_id', '=', customer_id), ('line_id.state', '=', 'process'), ('product_id.product_sample_location', '=', location_id)]
        customer_sale_lines = self.env['customer.sale.line'].search(search_list)
        pick_add_search_list = [('partner_id', '=', customer_id), ('state', '=', 'draft'), ('product_sample_location', '=', location_id)]
        batar_stock_pick_add = self.env['stock.pick.add'].search(pick_add_search_list)
        for line in customer_sale_lines:
            # change_qty 可以大于或者小于0，exchange_qty 值只会大于0
            if line.change_qty == 0 and line.exchange_qty == 0:
                continue
            else:

                # 若单据的状态为pick,换货不操作
                if line.state == "pick":

                    exchange_qty = line.exchange_qty
                    add_qty = line.exchange_qty
                    if line.change_qty > 0:
                        add_qty += line.change_qty
                    else:
                        # exchange_qty -= line.change_qty
                        # 退货
                        result, change_qty_need = self.confirm_change_pick_return(line, abs(line.change_qty), 'back')
                        if not result:
                            result, change_qty_need = self.confirm_change_pack_return(line, change_qty_need)
                            if not result:
                                result, change_qty_need = self.confirm_change_out_return(line, change_qty_need)
                                if not result:
                                    raise UserError(
                                        u"分拣中，%s还剩下%s个不能退，请手动后台操作" % (line.product_id.default_code, change_qty_need))
                    # 判断是否退货
                    old_exchange_qty = exchange_qty
                    if exchange_qty > 0:
                        result, exchange_qty = self.confirm_change_pick_return(line, exchange_qty, 'exchange')
                        add_qty -= (old_exchange_qty - exchange_qty)
                        if not result:
                            result, exchange_qty = self.confirm_change_pack_return(line, exchange_qty)
                            if not result:
                                result, exchange_qty = self.confirm_change_out_return(line, exchange_qty)
                                if not result:
                                    raise UserError(u"分拣中，%s还剩下%s个不能退，请手动后台操作" % (line.product_id.default_code, exchange_qty))
                    if add_qty > 0:
                        batar_stock_pick_add = self.create_stock_pick_add(user.current_customer, location_id, line, batar_stock_pick_add, add_qty)
                        if not batar_stock_pick_add:
                            raise  UserError(u"创建补货单失败,请联系管理人员")
                    line.change_qty = 0
                    line.exchange_qty = 0

                elif line.state == "pack":
                    exchange_qty = line.exchange_qty
                    add_qty = line.exchange_qty
                    if line.change_qty > 0:
                        add_qty += line.change_qty
                    else:
                        exchange_qty -= line.change_qty

                    if exchange_qty > 0:
                        result, change_qty = self.confirm_change_pack_return(line, exchange_qty)
                        if not result:
                            result, change_qty = self.confirm_change_out_return(line, exchange_qty)
                            if not result:
                                raise UserError(u"待验，%s还剩下%s个不能退，请手动后台操作" % (line.product_id.default_code, exchange_qty))
                    if add_qty > 0:
                        batar_stock_pick_add = self.create_stock_pick_add(user.current_customer, location_id, line, batar_stock_pick_add, add_qty)
                        if not batar_stock_pick_add:
                            raise UserError(u"创建补货单失败,请联系管理人员")

                    line.change_qty = 0
                    line.exchange_qty = 0
                elif line.state == 'out':
                    exchange_qty = line.exchange_qty
                    add_qty = line.exchange_qty
                    if line.change_qty > 0:
                        add_qty += line.change_qty
                    else:
                        exchange_qty -= line.change_qty

                    if exchange_qty > 0:
                        result, abs_change_qty = self.confirm_change_out_return(line, exchange_qty)
                        if not result:
                            raise UserError(u"待付款，%s还剩下%s个不能退，请手动后台操作" % (line.product_id.default_code, exchange_qty))
                    if add_qty > 0:
                        batar_stock_pick_add = self.create_stock_pick_add(user.current_customer, location_id, line, batar_stock_pick_add, add_qty)
                        if not batar_stock_pick_add:
                            raise UserError(u"创建补货单失败,请联系管理人员")
                    line.change_qty = 0
                    line.exchange_qty = 0
                elif line.state == 'delivery':
                    if line.change_qty > 0:
                        batar_stock_pick_add = self.create_stock_pick_add(user.current_customer, location_id, line, batar_stock_pick_add, add_qty)
                        if not batar_stock_pick_add:
                            raise UserError(u"创建补货单失败,请联系管理人员")

                        line.change_qty = 0
                    if line.exchange_qty > 0 or line.change_qty < 0 :
                        raise UserError(u"此状态不能在pad上退货，请联系业务人员")
        if batar_stock_pick_add:
            batar_stock_pick_add.confirm()
            batar_stock_pick_add.generate_pick_pack_out()
        # return self.get_one_page_tab_location_confirm_order(offset, limit, location_id, '')
        return True

    @api.model
    def confirm_change_pick_return(self, order_line=None, abs_change_qty=0, type='back'):
        ''''''
        if not order_line and abs_change_qty:
            return False, abs_change_qty
        pick_ids = order_line.pick_ids
        search_list = [('picking_id', 'in', [line.id for line in pick_ids]), ('product_id', '=', order_line.product_id.id), ('picking_id.state', '!=', 'done')]
        stock_operations = self.env['stock.pack.operation'].search(search_list)
        if type == 'exchange':
            for stock_operation in stock_operations:
                if stock_operation.product_qty >= abs_change_qty:
                    abs_change_qty = 0

                    break
                else:
                    abs_change_qty -= stock_operation.product_qty
        elif type == 'back':
            for stock_operation in stock_operations:
                can_return_qty = int(stock_operation.product_qty - stock_operation.qty_return)
                if abs_change_qty > can_return_qty:
                    stock_operation.qty_return += can_return_qty

                    abs_change_qty -= can_return_qty
                else:
                    stock_operation.qty_return += abs_change_qty
                    # order_line.order_qty -= abs_change_qty
                    abs_change_qty = 0
                    break
        if int(abs_change_qty) != 0:
            return False, abs_change_qty
        order_line.change_qty = 0
        order_line.exchange_qty = 0
        return True, abs_change_qty

    @api.model
    def confirm_change_pack_return(self, order_line=None, abs_change_qty=0):
        ''''''
        if not order_line and abs_change_qty:
            return False, abs_change_qty
        pack_ids = order_line.pack_ids
        search_list = [('picking_id', 'in', [line.id for line in pack_ids]), ('product_id', '=', order_line.product_id.id),
                       ('picking_id.state', '!=', 'done')]
        stock_operations = self.env['stock.pack.operation'].search(search_list)
        for stock_operation in stock_operations:
            can_return_qty = int(stock_operation.product_qty - stock_operation.qty_return)
            if abs_change_qty > can_return_qty:
                stock_operation.qty_return += can_return_qty

                abs_change_qty -= can_return_qty
                stock_operation.qty_done = stock_operation.product_qty - stock_operation.qty_return
            else:
                stock_operation.qty_return += abs_change_qty
                stock_operation.qty_done = stock_operation.product_qty - stock_operation.qty_return

                abs_change_qty = 0

                break

        if int(abs_change_qty) != 0:
            return False, abs_change_qty
        order_line.change_qty = 0
        order_line.exchange_qty = 0
        return True, abs_change_qty

    @api.model
    def confirm_change_out_return(self, order_line=None, abs_change_qty=0):
        ''''''
        if not order_line and abs_change_qty:
            return False, abs_change_qty
        out_ids = order_line.out_ids
        search_list = [('picking_id', 'in', [line.id for line in out_ids]), ('product_id', '=', order_line.product_id.id),
                       ('picking_id.state', '!=', 'done')]
        stock_operations = self.env['stock.pack.operation'].search(search_list)
        for stock_operation in stock_operations:
            can_return_qty = int(stock_operation.product_qty - stock_operation.qty_return)
            if abs_change_qty > can_return_qty:
                stock_operation.qty_return += can_return_qty
                abs_change_qty -= can_return_qty
                stock_operation.qty_done = stock_operation.product_qty - stock_operation.qty_return
                # order_line.order_qty -= can_return_qty
            else:
                stock_operation.qty_return += abs_change_qty
                # order_line.order_qty -= abs_change_qty
                abs_change_qty = 0
                stock_operation.qty_done = stock_operation.product_qty - stock_operation.qty_return
                break

        if int(abs_change_qty) != 0:
            return False, abs_change_qty
        order_line.change_qty = 0
        order_line.exchange_qty = 0
        return True, abs_change_qty
    @api.model
    def cancel_all_order(self, offset=0, limit=20, location_id=None):
        '''取消订单'''
        if not location_id:
            return False
        user = self.env['res.users'].search([('id', '=', self._context['uid'])])
        customer_id = user.current_customer and user.current_customer.id
        if not customer_id:
            return  False
        search_list = [('line_id.partner_id', '=', customer_id), ('line_id.state', '=', 'process'), ('product_id.product_sample_location', '=', location_id)]
        customer_sale_lines = self.env['customer.sale.line'].search(search_list)
        pick_ids = []
        for customer_sale_line in customer_sale_lines:
            pick_ids += [line.id for line in customer_sale_line.pick_ids if (line.state != 'done' and line.state != 'cancel')]
        pick_ids = list(set(pick_ids))
        self.env['stock.picking'].search([('id', 'in', pick_ids)]).action_cancel()
        pack_ids = []
        for customer_sale_line in customer_sale_lines:
            pack_ids += [line.id for line in customer_sale_line.pack_ids if
                         (line.state != 'done' and line.state != 'cancel')]
        pack_ids = list(set(pack_ids))
        self.env['stock.picking'].search([('id', 'in', pack_ids)]).action_cancel()
        out_ids = []
        for customer_sale_line in customer_sale_lines:
            out_ids += [line.id for line in customer_sale_line.pack_ids if
                         (line.state != 'done' and line.state != 'cancel')]
        out_ids = list(set(out_ids))
        self.env['stock.picking'].search([('id', 'in', out_ids)]).action_cancel()
        customer_sale_lines.unlink()
        confirm_order = self.get_confirm_order(offset, limit, None, '')
        if confirm_order:
            return confirm_order
        else:
            return 'no_data'





