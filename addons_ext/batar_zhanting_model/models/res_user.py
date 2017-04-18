# -*- coding: utf-8 -*-

from openerp import models,fields

class res_partner(models.Model):
    _inherit = 'res.partner'
    customer_code = fields.Char(string='customer code')


class res_user(models.Model):
    _inherit ='res.users'

    product_sample_location = fields.Many2many('stock.location','users_product_sample_location','user_id','location_id',string='product sample location')
    current_customer = fields.Many2one('res.partner',string='current customer')
    recent_customer = fields.One2many('recent.customer','user_id',string='recent customer' )

class recent_customer(models.Model):
    _name = 'recent.customer'
    _order = 'id desc'
    user_id = fields.Many2one('res.users', ondelete='cascade', string='users')
    customer = fields.Many2one('res.partner', string='recent customer')

