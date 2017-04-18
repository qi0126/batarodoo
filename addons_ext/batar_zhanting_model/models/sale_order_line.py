# -*- coding: utf-8 -*-

from openerp import models,fields

class sale_order_line(models.Model):

    _inherit="sale.order.line"

    def _get_top_product_cate(self):
        if self.product_id:
            top_product_cate = None
            product_cate = self.product_id.categ_id
            while product_cate:
                if product_cate.top_cate:
                    top_product_cate = product_cate
                    break
                product_cate = product_cate.parent_id

            if top_product_cate:
                self.top_product_cate = top_product_cate


    top_product_cate = fields.Many2one('product.category',compute="_get_top_product_cate",store=True,string='top product category')