# -*- coding: utf8 -*-
from openerp import api, fields, models
class Picking(models.Model):
    _inherit = 'stock.pack.operation'

    @api.model
    def create(self, vals):
        if vals.get('picking_id') and vals.get('product_qty'):
            pick_type = self.env['stock.picking.type'].with_context(lang='en').sudo().search(
                [('name', 'ilike', 'pick')]).ids
            current_type = self.env['stock.picking'].browse(vals['picking_id']).picking_type_id
            if current_type.id not in pick_type:
                vals['qty_done'] = vals['product_qty']
        res = super(Picking, self).create(vals)
        return res