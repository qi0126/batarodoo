# -*- coding: utf-8 -*-
from openerp import api, fields, models

class ProductImages(models.Model):
    _name = 'batar.product.images'

    name = fields.Char(string='Name')
    datas_fname = fields.Char(string='datas_fname')
    sequence = fields.Integer(string='Sequence')
    image = fields.Binary(string='Image', attachment=True)
    product_id = fields.Many2one('product.product', string='Product')

class Product(models.Model):
    _inherit = 'product.product'

    multi_images = fields.One2many('batar.product.images', 'product_id', string='Images')