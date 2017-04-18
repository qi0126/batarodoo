# -*- coding: utf-8 -*-
from openerp import api, fields, models

class BatarOperation(models.Model):
    _inherit = 'stock.pack.operation'

    qty_return = fields.Float(string="Qty Return", default=0.0)

class BatarAdjustment(models.Model):
    _inherit = 'batar.location.adjustment'

    reverse_id = fields.Many2one('stock.picking', string='Return order', readonly=True, states={'draft': [('readonly', True)]})

class BatarPick(models.Model):
    _inherit = 'stock.picking'

    adjustment_id = fields.One2many('batar.location.adjustment', 'reverse_id', string='Return orders')

    @api.multi
    def do_new_transfer(self):
        for picking in self:
            if picking.pack_operation_ids:
                if all([x.qty_done == 0.0 for x in picking.pack_operation_ids]):
                    return picking.move_lines_related.action_cancel()
                else:
                    for op in picking.pack_operation_ids:
                        if op.qty_done == 0:
                            picking.write({'pack_operation_ids': [(2,op.id)]})
                            # for i in op.linked_move_operation_ids:
                            #     move = i.move_id
                            #     move.action_cancel()
                            # move = op.linked_move_operation_ids[0].move_id
                            # op.unlink()
                            # move.action_cancel()

        res = super(BatarPick, self).do_new_transfer()
        return res
    # @api.model
    # def check_backorder(self, picking):
    #     return False





