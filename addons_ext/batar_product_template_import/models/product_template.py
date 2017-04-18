#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:product_template.py
@date:2016/11/8 18:26
"""

from openerp import  models,fields

class product_template(models.Model):

    _inherit = 'product.template'

    import_code  =fields.Char(string='import code')
    _sql_constraints = [
        ('unique', 'unique(import_code)', u'导入的编号必须唯一'),
    ]