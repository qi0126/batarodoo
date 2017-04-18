# -*- coding: utf-8 -*-
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp

class Lailiao_order(models.Model):
    _name = 'batar.lailiao'

    name = fields.Char(string='Name', required=True, default='New')
    description = fields.Text(string='Description')
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True, states={'draft': [('readonly', 'False')]})
    credit = fields.Float(string="Credit", readonly=True, states={'draft': [('readonly', 'False')]}, digits=dp.get_precision('Lai liao'))
    debit = fields.Float(string="Debit", readonly=True, states={'draft': [('readonly', 'False')]}, digits=dp.get_precision('Lai liao'))
    weight = fields.Float(string="R-weight", readonly=True, states={'draft': [('readonly', 'False')]}, digits=dp.get_precision('Lai liao'))
    assay = fields.Float(string="Assay", readonly=True, states={'draft': [('readonly', 'False')]})
    sale_id = fields.Many2one('sale.order', string="Reference Oder", readonly=True, states={'draft': [('readonly', 'False')]})
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lailiao') or "New"
            res = super(Lailiao_order, self).create(vals)
            return  res
