# -*- coding: utf-8 -*-
from openerp import api, fields, models

class Package(models.Model):
    _name = 'batar.package'

    name = fields.Char(string='Name', default='/')
    partner_id = fields.Many2one('res.partner', string='Partner')
    product_id = fields.Many2one('product.product', string='Product')
    product_code = fields.Char(string='Product Code')
    weight = fields.Float(string="Weight")
    net_weight = fields.Float(string='Net Weight')
    qty = fields.Integer(string='Qty')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done'), ('cancel', 'Cancel')], default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', '/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('batar_package') or '/'
        res = super(Package, self).create(vals)
        return res

    @api.multi
    @api.onchange('product_id')
    def onchange_product_code(self):
        self.ensure_one()
        if self.product_id:
            self.product_code = self.product_id.default_code