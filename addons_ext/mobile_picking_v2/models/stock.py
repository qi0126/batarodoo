# -*- coding: utf-8 -*-
from openerp import api, fields, models

class Quant(models.Model):
    _inherit = 'stock.quant'

    location_sequence = fields.Integer(string='Sequence')

    @api.model
    def create(self, vals):
        if vals.get('location_id'):
            location = self.env['stock.location'].browse(vals['location_id'])
            if location.barcode:
                vals['location_sequence'] = int(location.barcode.replace('-', ''))
        res = super(Quant, self).create(vals)
        return res
    @api.multi
    def write(self, vals):
        if vals.get('location_id'):
            location = self.env['stock.location'].browse(vals['location_id'])
            if location.barcode:
                vals['location_sequence'] = int(location.barcode.replace('-', ''))
        res = super(Quant, self).write(vals)
        return res
    @api.model
    def apply_removal_strategy(self, quantity, move, ops=False, domain=None, removal_strategy='fifo'):
        if removal_strategy == 'fifo':
            order = 'location_sequence'
            return self._quants_get_order(quantity, move, ops=ops, domain=domain, orderby=order)
        else:
            res = super(Quant, self).apply_removal_strategy(quantity, move, ops=False, domain=None, removal_strategy='fifo')
            return res
class Pick(models.Model):
    _inherit = 'stock.picking'
    # @api.multi
    # def do_new_transfer(self):
