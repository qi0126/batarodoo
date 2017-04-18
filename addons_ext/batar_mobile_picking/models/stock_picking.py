# -*- coding: utf-8 -*-
from openerp import models, fields,api

class StockPick(models.Model):
    _inherit = 'stock.picking'

    sample_location = fields.Many2one('stock.location', string='Sample Location')
    mobile_user = fields.Many2one('res.users', string='Pick user')

    @api.multi
    def action_delivery_done(self):
        super(StockPick, self).action_delivery_done()
        pick_type_ids = self.env['stock.picking.type'].with_context(lang='en').search([('name', 'ilike', 'Pick')]).ids
        for line in self:
            if line.picking_type_id.id in pick_type_ids:
                op_ids = line.pack_operation_product_ids.ids
                pick_lines = self.env['mobile.picking.line'].search([('operation_id', 'in', op_ids)])
                if pick_lines:
                    pick_lines.write({'state': 'delivery'})
                    pick_task = pick_lines[0].pick_id
                    state = set([x.state for x in pick_task.line_ids])
                    if list(state) == ['delivery']:
                        pick_task.write({'state': 'done'})


    @api.multi
    @api.onchange('pack_operation_product_ids')
    def onchange_sample_location(self):
        """
        根据操作明细行中产品的样品库来改变整个分拣单的样品库
        """
        for line in self:
            if line.pack_operation_product_ids:
                self.sample_location = line.pack_operation_product_ids[0].product_id.product_sample_location