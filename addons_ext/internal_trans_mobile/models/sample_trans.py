# -*- coding: utf-8 -*-
from openerp import api, fields, models

class SampleTrans(models.Model):
    _inherit = 'batar.sample.trans'

    @api.multi
    def action_part_confirm(self):
        res = super(SampleTrans, self).action_part_confirm()
        trans_obj = self.env['internal.trans.mobile']
        trans_order = trans_obj.create({'state': 'draft', 'trans_id': self.id})
        operations = [x.pack_operation_product_ids for x in self.picking_ids]
        lines = []
        for op in operations:
            vals = {
                'product_id': op.product_id.id,
                'qty': op.product_qty,
                'src_location': op.location_id.id,
                'dest_location': op.location_dest_id.id,
                'state': 'draft',
                'op_id': op.id,
            }
            lines.append((0,0,vals))
        trans_order.write({'line_ids': lines})
        return res
