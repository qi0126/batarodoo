# -*- coding:utf-8 -*-
from openerp import api, fields, models

class VendorInfo(models.Model):
    _name = 'batar.product.vendor'

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    code = fields.Char(string='Product Code', required=True)
    work_days = fields.Float(string="Work days")
    uom_id = fields.Many2one('product.uom', string="Uom")
    desc = fields.Text(string='Description')

class Product(models.Model):
    _inherit = 'product.product'

    vendor_info = fields.One2many('batar.product.vendor', 'product_id', string='Vendor info')