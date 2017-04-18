#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo10
@author:cloudy
@site:
@file:counter.py
@date:2017/3/18 13:59
"""
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
class Counter(http.Controller):
    @http.route([
        '/counter/list',
        '/counter'
    ], type='http', auth='user',website=True)
    def list(self, **kw):
        """
        显示柜台
        :param kw:
        :return:
        """
        counter_obj = request.env['company.counter']
        """获得可用的柜台"""
        counters = counter_obj.search([('active', '=', True)])
        print counters
        return http.request.render('company_counter.counter_list', {
            'counters': counters
        })

    @http.route([
        '/counter/product/inactive/'
    ], type='json', auth='user', website=True)
    def product_inactive(self, **kwargs):
        """
        :param kwargs:
        :return:
        """
        print kwargs
        counter_id = int(kwargs.get("counter", "0"))
        product_id = int(kwargs.get("product", "0"))
        if counter_id > 0 and product_id >0 :
            counter_product_obj = http.request.env['counter.product']
            return counter_product_obj.search([('counter_id','=',counter_id),('product','=',product_id)]).write({"active": False})
        else:
            return  False

    @http.route([
        '/counter/<int:counter_id>',
        '/counter/<int:counter_id>/page/<int:page>'
    ], type='http', auth="user", website=True)
    def display_counter(self, counter_id=0, page=0, ppg=False, **post):
        """
        :param counter_id:
        :param page:
        :param ppg:
        :param post:
        :return:
        """
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        """返回结果"""
        return_values = {}
        url = '/counter'
        if counter_id > 0:
            counter_obj = request.env['company.counter']
            counter = counter_obj.browse(counter_id)
            return_values['counter'] = counter
            counter_product_obj = http.request.env['counter.product']
            domain = [('active', '=', True), ('counter_id','=',counter_id)]
            product_count = counter_product_obj.search_count(domain)
            pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            return_values['pager'] = pager
            products = counter_product_obj.search(domain, limit=ppg, offset=pager['offset'])
            if len(products):
                return_values['products'] = products

        return http.request.render('company_counter.counter_info', return_values)




