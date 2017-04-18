# -*- coding: utf-8 -*-

from openerp import api, fields, models

class Putaway(models.Model):
    _inherit = 'product.putaway'


    def _get_putaway_options(self):
        return [('fixed', 'Fixed Location'), ('dynamic', 'Dynamic Location')]

    dynamic_type = fields.Selection([('vacancy', 'Vacancy'), ('add', 'Make up')], string='Dynamic Type')

class Product(models.Model):
    _inherit = 'product.product'

    batar_volume = fields.Integer(string='Volume', help="the physical location of each product")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    template_volume = fields.Integer(string='Volume', help="the physical location of each product")

class Location(models.Model):
    _inherit = 'stock.location'

    @api.multi
    def _get_inuse_volume(self):
        total = 0.0
        return total

    location_volume = fields.Integer(string='Volume')
    inuse_volume = fields.Integer(string='Inuse Volume', compute=_get_inuse_volume)