# -*- coding: utf-8 -*-
from openerp import models, api, fields

class BatarPicking(models.Model):
    _inherit = 'stock.picking'

    is_delivery = fields.Boolean(string='Delivery Done', default=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('done', 'Done'),
        ('delivery done', 'Delivery Done'),
    ])

    @api.multi
    def action_delivery_done(self):
        self.write({'is_delivery': True,})

class BatarSale(models.Model):
    _inherit = 'sale.order'


    picking_state = fields.Selection([('waiting', 'Waiting'), ('another', 'Waiting Another'), ('picking', 'Picking'), ('pay', 'Pay'), ('delivery', 'delivery'), ('done', 'Done')])



    @api.multi
    @api.depends('procurement_group_id')
    def get_picking_state(self):
        for order in self:
            pick_type = self.env['stock.picking.type'].with_context(lang='en').search([('name', 'ilike', 'pick')])[0]
            pack_type = self.env['stock.picking.type'].with_context(lang='en').search([('name', 'ilike', 'pack')])[0]
            out_type = self.env['stock.picking.type'].with_context(lang='en').search([('name', 'ilike', 'delivery orders')])[0]
            picking_ids = self.env['stock.picking'].search([('group_id', '=', order.procurement_group_id.id), ('picking_type_id', '=', pick_type.id), ('state', '!=', 'done')])
            packing_ids = self.env['stock.picking'].search(
                [('group_id', '=', order.procurement_group_id.id), ('picking_type_id', '=', pack_type.id),
                 ('state', '!=', 'done')])
            out_ids = self.env['stock.picking'].search(
                [('group_id', '=', order.procurement_group_id.id), ('picking_type_id', '=', out_type.id),
                 ('state', '!=', 'done')])
            delivery_ids = self.env['stock.picking'].search(
                [('group_id', '=', order.procurement_group_id.id), ('picking_type_id', '=', out_type.id),
                 ('is_delivery', '=', False)])

            if picking_ids:
                for i in picking_ids:
                    if i.state == 'confirmed':
                        order.picking_state = 'another'
                        break
                    else:
                        order.picking_state = 'waiting'
                continue
            elif packing_ids and not picking_ids:
                order.picking_state = 'picking'
                continue
            elif out_ids and not packing_ids:
                order.picking_state = 'pay'
                continue
            elif delivery_ids and not out_ids:
                order.picking_state = 'delivery'
            elif not delivery_ids:
                order.picking_state = 'done'
