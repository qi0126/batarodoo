# -*- coding: utf-8 -*-

from openerp import models, fields, api
import re
from datetime import datetime, timedelta


class batar_batch_sale_order(models.Model):
    _name = 'batar.batch.sale.order'

    @api.model
    def add_product_to_order(self,params={}):
        """添加产品到销售订单，如果没有销售订单创建一个销售订单"""
        res = {
            'msg': "",
            'code': 'success',
            'data': []
        }
        user = self.env.user
        dt = fields.Datetime.to_string(datetime.utcnow() - timedelta(seconds=60*60*24))
        if user.current_customer:
            partner_id = user.current_customer.id
            sale_order = self.env['sale.order'].search([('order_type', '=', 'batch'),('user_id', '=', self.env.uid), ('partner_id', '=', partner_id), ('state', '=', 'draft'),('create_date', '>', dt)])
            if not sale_order:

                vals = {
                    "order_type":"batch",
                    'partner_id':partner_id,
                }

                vals['partner_id'] = user.current_customer.id
                material_price_line = []
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
                vals['material_price_line'] = material_price_line
                sale_order = self.env['sale.order'].create(vals)
            order_lines = params.get('data',[])
            order_line_obj = self.env['sale.order.line']
            for line in order_lines:
                product_id = line.get('id','')
                qty= line.get('qty',0)
                if product_id:
                    product_id = int("%s" % product_id)

                    order_line = order_line_obj.search([('order_id','=',sale_order.id),('product_id','=',product_id)])
                    if order_line:
                        if int(qty)==0:
                            order_line.unlink()
                        else:
                            order_line.product_uom_qty = qty
                    else:
                        if int(qty) >=1:
                            product = self.env['product.product'].search([('id','=',product_id)])
                            line_vals = {
                                'product_id':product.id,
                                'product_uom_qty':  qty,
                            }
                            for attribute_value_id in product.attribute_value_ids:
                                if attribute_value_id.attribute_id.code == "weight":
                                    m = re.match(r"(^[0-9]\d*\.\d|\d+)", attribute_value_id.name)
                                    if m:
                                        standard_weight = m.group(1)
                                        line_vals['standard_weight'] = float(standard_weight)
                                        line_vals['all_weights'] = line_vals['standard_weight'] * qty
                            sale_order.write({'order_line':[(0,0,line_vals)]})
        else:
            res['msg']=u"请选择一个客户"
            res["code"] = 'failed'


        return res
    @api.model
    def get_product_products_filter(self,params={}):
        """根据款式的属性获得产品规格"""
        res = {
            'msg': "",
            'code': 'failed',
            'data': []
        }
        product_tmpl_id = params.get("temp_id",None)
        filter_products = []
        product_list_info = []
        if product_tmpl_id:
            product_template = self.env['product.template'].search([('id','=',product_tmpl_id)])
            attribute_lines = product_template.attribute_line_ids
            select_attributes = params.get("data",[])
            attribute_value_id_list = []
            for attribute in select_attributes:
                attribute_data = attribute.get('data',[])

                if attribute_data:
                    attribute_value_id_list +=[int(line) for line in attribute_data]
                else:
                    attribute_id =attribute.get('id',"")
                    if attribute_id:
                        product_attribute = self.env['product.attribute'].search([('id','=',attribute_id)])
                        print product_attribute.value_ids
                        attribute_value_id_list += [line.id for line in product_attribute.value_ids]
            if attribute_value_id_list:
                attribute_value_id_set = set(attribute_value_id_list)
                products = self.env['product.product'].search([('product_tmpl_id', '=', product_tmpl_id)])
                for product in products:
                    ids = [line.id for line in product.attribute_value_ids]
                    if set(ids).issubset(attribute_value_id_set):
                        filter_products.append(product)
            else:
                pass
        if  filter_products:
            for product in filter_products:
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
                attribute_value_ids = product.attribute_value_ids
                for attribute_value_id in attribute_value_ids:
                    if attribute_value_id.attribute_id.code == "weight":
                        m = re.match(r"(^[0-9]\d*\.\d|\d+)", attribute_value_id.name)
                        if m:
                            standard_weight = m.group(1)
                            info['standard_weight'] = float(standard_weight)
                product_list_info.append(info)
        if product_list_info:
            res['data'] = product_list_info
            res['code'] = "success"
        else:
            res["msg"] = u"没有符合要求的产品"

        return res
    @api.model
    def get_product_template_list(self,name="",offset=0, limit=20 ):
        """获得产品款式列表"""
        res = {'code': 'failed', 'data': []}
        search_list = []
        if name:
            search_list= [('name','ilike',name)]
        product_templates = self.env['product.template'].search(search_list,limit=limit,offset=limit*offset,order="id desc")
        data = []
        for line in product_templates:
            data.append({
                'id':line.id,
                'name':line.name
            })
        if data:
            res['code'] = 'success'
            res['data'] = data
        return  res
    @api.model
    def get_product_template_attributes(self,product_tmpl_id=""):
        """获得产品款式属性"""
        res = {'code': 'failed', 'data': []}
        if product_tmpl_id:
            data = []
            attribute_lines = self.env['product.attribute.line'].search([('product_tmpl_id','=',product_tmpl_id)])
            for line in attribute_lines:
                data_dict = {}
                data_dict['name'] = line.attribute_id.name
                data_dict['id'] = line.attribute_id.id
                data_dict['data'] = []
                for value_line in line.value_ids:
                    value_list =  {}
                    value_list['id'] = value_line.id
                    value_list['name'] = value_line.name
                    data_dict["data"].append(value_list)

                data.append(data_dict)
        if data:
            res['code'] = 'success'
            res['data'] = data

        return res


    @api.model
    def get_product_product_list(self,product_tmpl_id="",offset=0, limit=20 ):
        """根据某个款式获得所有的规格"""
        res = {'code': 'failed', 'data': []}
        if product_tmpl_id:
            products = self.env['product.product'].search([('product_tmpl_id','=',product_tmpl_id)],limit=limit,offset=limit*offset,order="id desc")
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
                product_list_info.append(info)
            if product_list_info:
                res['code'] = 'success'
                res['data'] = product_list_info
        return res

    @api.model
    def get_order_product_template_list(self):
        """获得客户订单中的产品款式"""
        res = {'code':'failed','data':[]}
        user = self.env.user
        if user and user.current_customer:
            partner_id = user.current_customer.id
            search_list = [('order_type', '=', 'batch'), ('user_id', '=', self.env.uid), ('partner_id', '=', partner_id), ('state', '=', 'draft')]
            order = self.env["sale.order"].search(search_list,limit=1)
            order_line = order.order_line
            template_ids = [line.product_id.product_tmpl_id.id for line in order_line]
            product_templates = self.env['product.template'].search([('id','in',template_ids)])
            data = []
            for product_template in product_templates:
                data.append({
                    'id':product_template.id,
                    'name':product_template.name
                })
            if data:
                res['code']='success'
                res['data'] = data
        return res
    @api.model
    def get_order_product_product_list(self,product_tmpl_id=""):
        """获得客户订单中某个款式下所有的规格"""

        res = {'code': 'failed', 'data': []}
        user = self.env.user
        if user and user.current_customer and product_tmpl_id:
            partner_id = user.current_customer.id
            search_list = [('order_type', '=', 'batch'), ('user_id', '=', self.env.uid), ('partner_id', '=', partner_id), ('state', '=', 'draft')]
            order = self.env["sale.order"].search(search_list, limit=1)
            order_lines = self.env['sale.order.line'].search([('order_id','=',order.id),('product_id.product_tmpl_id.id','=',product_tmpl_id)])
            product_list_info = []
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
                product_list_info.append(info)
            if product_list_info:
                res['code'] = 'success'
                res['data'] = product_list_info
        return res

    @api.model
    def change_current_customer(self, customer_info="", customer_id=None,offset=0, limit=20):
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
                user = self.env['res.users'].search([('id', '=', self.env.uid)])

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
        res = self.get_current_user_info(offset, limit)
        res['code'] = 'success'
        return res
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
    def get_current_user_info(self, offset=0, limit=20):
        '''获得当前用户的当前客户，最近客户，柜台产品信息'''

        user = self.env['res.users'].search([('id', '=', self.env.uid)])
        res = {}
        current_customer = self.get_current_customer(user)
        recent_customer_list = self.get_recent_customer(user)

        if current_customer:
            res['current_customer'] = current_customer
        if recent_customer_list:
            res['recent_customer_list'] = recent_customer_list
        return res
    @api.model
    def get_customter_list(self,offset=0,limit=20, customerInfo=""):
        '''获得客户列表'''
        res = {"customer_info":[],'page_list':[]}
        search_list = [('is_company', '=', True), ('customer', '=', True)]
        if customerInfo:
            search_list = ['|', '|', ('name', 'like', customerInfo), ('customer_code', 'like', customerInfo),
                           ('mobile', 'like', customerInfo), ('is_company', '=', True), ('customer', '=', True)]
        all_count = self.env['res.partner'].search_count(search_list)
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

            if offset - 2 < 0:
                page_list = page_list[0:5]
            elif offset + 2 >= page_num:
                page_list = page_list[page_num - 5:page_num]
            else:
                page_list = page_list[offset - 2:offset + 3]
        else:
            pass
        res["page_list"] = page_list
        customer_list = self.env['res.partner'].search(search_list, offset=offset * limit, limit=limit)
        for line in customer_list:
            customer_dict = {}
            customer_dict['id'] = line.id
            customer_dict['name'] = line.name
            customer_dict['phone'] = line.mobile or "-"
            customer_dict['customer_code'] = line.customer_code or "-"
            res["customer_info"].append(customer_dict)
        return res
