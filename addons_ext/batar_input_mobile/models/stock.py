# -*- coding: utf-8 -*-
from openerp import api, fields, models
import re
from openerp.exceptions import UserError
from openerp.tools.translate import _
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp

class StockMove(models.Model):
    _inherit = 'stock.move'

    input_id = fields.Many2one('batar.input.mobile', string='Mobile Input')
    net_weight = fields.Float(string='Second Qty', digits=dp.get_precision('Batar Price'))

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    net_weight = fields.Float(string='Second Qty', digits=dp.get_precision('Batar Price'))

    @api.model
    def create(self, vals):
        if vals.get('product_id') and vals.get('qty'):
            product = self.env['product.product'].browse(vals['product_id'])
            attribute_value_ids = product.attribute_value_ids
            standard_weight = 0.0
            for a in attribute_value_ids:
                if a.attribute_id.code == "weight":
                    m = re.match(r"(^[0-9]\d*\.\d|\d+)", a.name)
                    weight = m.group(1)
                    standard_weight = float(weight)
                    break
            vals['net_weight'] = standard_weight * vals.get('qty')
        res = super(StockQuant, self).create(vals)
        return res
    @api.multi
    def write(self, vals):
        # if vals.get('product_id') and vals.get('qty'):
        if vals.get('qty'):
            product = self.product_id
            # product = self.env['product.product'].browse(vals['product_id'])
            attribute_value_ids = product.attribute_value_ids
            standard_weight = 0.0
            for a in attribute_value_ids:
                if a.attribute_id.code == "weight":
                    m = re.match(r"(^[0-9]\d*\.\d|\d+)", a.name)
                    weight = m.group(1)
                    standard_weight = float(weight)
                    break
            vals['net_weight'] = standard_weight * vals.get('qty')
        res = super(StockQuant, self).write(vals)
        return res
    @api.model
    def quants_reserve(self, quants, move, link=False):
        toreserve = []
        reserved_availability = move.reserved_availability
        for quant, qty in quants:
            if qty <= 0.0 or (quant and quant.qty <= 0.0):
                raise UserError(_('You can not reserve a negative quantity or a negative quant.'))
            if not quant:
                continue
            new_quant = self._quant_split(quant, qty)
            quant.sudo().write({'qty': qty})
            toreserve.append(quant.id)
            reserved_availability += quant.qty
        #reserve quants
        if toreserve:
            self.browse(toreserve).sudo().write({'reservation_id': move.id})
        #check if move'state needs to be set as 'assigned'
        rounding = move.product_id.uom_id.rounding
        if float_compare(reserved_availability, move.product_qty, precision_rounding=rounding) == 0 and move.state in ('confirmed', 'waiting')  :
            self.env['stock.move'].browse([move.id]).write({'state': 'assigned'})
        elif float_compare(reserved_availability, 0, precision_rounding=rounding) > 0 and not move.partially_available:
            self.env['stock.move'].browse([move.id]).write({'partially_available': True})
        return True

