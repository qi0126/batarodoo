# -*- coding: utf-8 -*-
from openerp import api, fields, models

class batarsale(models.Model):
    _inherit = 'sale.order'

    picking_state = fields.Selection([('waiting', 'Waiting'), ('another', 'Waiting Another'), ('confirmed', 'Confirmed'), ('done', 'Done')], default='waiting', compute='get_picking_state')

    @api.multi
    @api.depends('procurement_group_id')
    def get_picking_state(self):
        self._context
        for order in self:
            order.picking_ids = self.env['stock.picking'].search([('group_id', '=', order.procurement_group_id.id)]) if order.procurement_group_id else []
            pick_instate = []
            pick_type = self.env['stock.picking.type'].with_context(lang='en').sudo().search([('name', 'ilike', 'pick')])[0]
            for i in order.picking_ids:
                if i.picking_type_id == pick_type and i.state == 'confirmed':
                    pick_instate.append(i.id)
            if len(pick_instate) > 0:
                order.picking_state = 'another'
            else:
                order.picking_state = 'confirmed'
        # pick_obj = self.env['stock.picking']
        # group = self.env['procurement.group'].search([('name', '=', self.name)])
        # pick_type = self.env['stock.picking.type'].search([('name', 'ilike', 'pick')])[0]
        # domain = [('group_id', '=', group.id), ('picking_type_id','=', pick_type.id), ('state', '=', 'confirmed')]
        # pick_order = pick_obj.search(domain)
        # if pick_order:
        #     self.picking_done = 'another'