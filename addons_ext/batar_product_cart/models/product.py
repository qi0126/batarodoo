# -*- coding:utf-8 -*-
from openerp import api, models, fields, exceptions

class product_product(models.Model):
    _inherit = 'product.product'

    add_cart = fields.Boolean(string='Add Cart', default=False)

    @api.multi
    def add_batar_cart(self):
        self.ensure_one()
        cart = self.env['batar.product.cart']
        vals = {}
        carts = cart.search([])
        # if len(carts):
        for c in carts:
            if c.product_id.id == self.id:
                raise exceptions.ValidationError(u'已添加!')
        # else:
        vals['product_id'] = self.id
        return cart.create(vals)