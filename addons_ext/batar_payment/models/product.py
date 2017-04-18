# -*- coding: utf-8 -*-
from openerp import fields, api, models

class Batar_product(models.Model):
    _inherit = 'product.template'

    process_cost = fields.Float(string="Base cost", help="Each product basic processing fee")