# -*- encoding: UTF-8 -*-

from openerp import models, fields


class ProductImage(models.Model):
    _name = 'product.image'
    _order = 'sequence, id DESC'

    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Name')
    image = fields.Binary(string='Image', attachment=True)
    product_id = fields.Many2one('product.template', string='Product')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    images = fields.One2many('product.image', 'product_id', 'Images')
