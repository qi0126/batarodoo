# -*- coding: utf-8 -*-
from openerp import models, api, fields
from openerp.exceptions import UserError

class Wizard_lines(models.TransientModel):
    _name = 'batar.return.wizard.line'

    product_id = fields.Many2one('product.product', string='Product')
    src_location = fields.Many2one('stock.location', string='Source Location')
    dest_location = fields.Many2one('stock.location', string='Dest Location')
    qty = fields.Integer(string='Qty')

class BatarReturn_wizard(models.TransientModel):
    _name = 'batar.return.wizard'

    product_code = fields.Char(string='Product Num')
    line_ids = fields.Many2many('batar.return.wizard.line', string='Move line')

    @api.onchange('product_code')
    def onchange_line(self):
        '''退货入存储库明细'''
        product_obj = self.env['product.product']
        quant_obj = self.env['stock.quant']
        location = self.env['stock.location']
        order = self.env['stock.picking'].browse(self._context.get('active_ids'))[0]
        inuse_location = []
        line_ids = []
        for line in self.line_ids:
            inuse_location.append(line.dest_location.id)
            line_ids.append((4, line.id, 0))
        # src_location = order.location_dest_id
        src_location = order.location_id
        if self.product_code:
            product = product_obj.search([('default_code', '=', self.product_code)])
            if not product:
                raise UserError(u'当前库位中无此编码的产品规格！')
            parent_location = product[0].product_sample_location.location_id
            res = []
            view_locs = self.env['stock.location'].search(
                [('location_id', '=', parent_location.id), ('usage', '=', 'view')])
            in_sample = quant_obj.search([('product_id', '=', product.id), ('location_id', '=', src_location.id)])
            qty_sample = sum([x.qty for x in in_sample]) - sum(
                [y.qty for y in self.line_ids if y.product_id == product])
            if qty_sample <= 0:
                raise UserError(u'当前库位无此产品，请确认后再输入！')
            else:
                vals = {
                    'product_id': product.id,
                    'qty': 1,
                    'src_location': src_location.id,
                }
                for loc in view_locs:
                    flag = False
                    if loc.child_ids:
                        for i in loc.child_ids:
                            if i.id in inuse_location:
                                continue
                            total = 0.0
                            for j in quant_obj.search([('location_id', '=', i.id)]):
                                total += j.product_id.product_volume * j.qty
                            if i.location_volume - total >= product.product_volume:
                                res.append(i.id)
                                vals['dest_location'] = i.id
                                flag = True
                                break
                        if flag:
                            break

                    else:
                        raise UserError('不存托盘库位！')
                if len(res) == 0:
                    raise UserError('所有储柜已满！')
                line_ids.append((0, 0, vals))
                self.line_ids = line_ids

    @api.multi
    def confirm(self):
        self.ensure_one()
        adjustment_obj = self.env['batar.location.adjustment']
        pick_order = self.env['stock.picking'].browse(self._context.get('active_ids'))[0]
        if self.line_ids:
            adj_order = adjustment_obj.create({'reverse_id': pick_order.id, 'location_id': self.line_ids[0].src_location.id})
            move_lines = []
            for line in self.line_ids:
                vals = {
                    'product_id': line.product_id.id,
                    'location_id': line.src_location.id,
                    'location_dest_id': line.dest_location.id,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uom_qty': line.qty,
                    'name': 'MO:adj',
                    'origin': 'Return:' + pick_order.name
                }
                move_lines.append((0,0,vals))
            adj_order.write({'move_ids': move_lines, 'state': 'process', 'is_sample': False})
            return {
                'type': 'ir.actions.act_window',
                'context': self._context,
                'res_model': 'batar.location.adjustment',
                'res_id': adj_order.id,
                'view_type': 'form',
                'view_mode': 'form,tree',
            }