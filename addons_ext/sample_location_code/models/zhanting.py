# -*- coding: utf-8 -*-
from openerp import api, fields, models

class Zhanting(models.Model):
    _inherit = 'zhanting'

    @api.model
    def get_one_page_tab_location(self, offset=0, limit=20, location_id=None, customer_id=None, default_code='',
                                  has_stock=False):
        """
        修改展厅界面中的查找功能
        如果输入小于五位数，则优先匹配货号
        """
        location = self.env['stock.location'].search([('id', '=', location_id)])
        tab_location = {}
        if default_code:
            if len(default_code) < 5:
                search_list = [('active', '=', True), ('location_id', '=', location.id), ('name', '=', default_code)]
                current_customer_product_dict = self.current_customer_product_dict(customer_id, location.id)
                all_count = self.env['sample.location.code'].search_count(search_list)
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

                products = self.env['sample.location.code'].search(search_list, offset=offset * limit, limit=limit).mapped('product_id')
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
            else:
                res = super(Zhanting, self).get_one_page_tab_location(offset=offset, limit=limit,
                                                                      location_id=location_id,
                                                                      customer_id=customer_id,
                                                                      default_code=default_code, has_stock=has_stock)
        else:
            res = super(Zhanting, self).get_one_page_tab_location(offset=offset, limit=limit, location_id=location_id,
                                                                      customer_id=customer_id, default_code=default_code, has_stock=has_stock)
        return res