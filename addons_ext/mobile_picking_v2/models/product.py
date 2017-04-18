# -*- coding: utf-8 -*-
from openerp import api, fields, models

class Product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def name_get(self):
        res = []
        for product in self:
            variant = ", ".join([v.name for v in product.attribute_value_ids])
            name = variant and "%s (%s)" % (product.name, variant) or product.name
            res.append((product.id, name))
        return res
