# -*- coding: utf-8 -*-
from openerp import fields, api, models

class Stock(models.Model):
    _inherit = 'stock.location'

    _sql_constraints = [('barcode_company_uniq', 'unique (barcode,company_id)', u'库位编号已存在！')]

