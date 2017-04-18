# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Quality(models.Model):
    _inherit = 'quality.order'

    sample_trans_id = fields.Many2one('batar.sample.trans', string='Quality Order')

class SampleTrans(models.Model):
    _inherit = 'batar.sample.trans'
    @api.multi
    def action_part_confirm(self):
        """生成入库质检单"""
        res = super(SampleTrans, self).action_part_confirm()
        if self.type =="out":
            for line in self:
                order_values = {}
                order_values['name'] = line.name
                order_values['partner_id'] = line.user_id.partner_id.id
                order_values['partner_person'] = line.shenhe_user.name
                order_values['partner_mobile'] = ""
                order_values['delivery_method'] = "internal_out"
                order_values['delivery_man'] = line.shenhe_user.name
                order_values['delivery_mobile'] = ''
                order_values['location_src_id'] = line.location_id.id
                order_values['location_dest_id'] = line.location_id.id
                order_values['state'] = 'wait_check'
                order_values['sample_trans_id'] = line.id
                line_values =[]
                for order_line in self.line_ids:
                    line_values.append((0, 0, {
                        'name': order_line.code,
                        'supplier_code':order_line.product_id.default_code,
                        'default_code': order_line.product_id.default_code,
                        'product_id': order_line.product_id.id,
                        'product_qty': order_line.qty,
                        'net_weight': order_line.net_weight,
                        'gross_weight': 0,
                        'must_check': True,
                        'state': 'wait_check',
                    }))
                order_values['line_ids'] = line_values
                self.env['quality.order'].create(order_values)
        return res
# class TransMobiel(models.Model):
#     _inherit = 'internal.trans.mobile'
#     plate = fields.Char(string='Plate name')
#
#     @api.model
#     def get_trans_task(self):
#         trans_obj = self.env['internal.trans.mobile']
#         draft_order = trans_obj.search([('state', '=', 'draft')], limit=1)
#         if draft_order and draft_order.line_ids:
#             # 存在任务，但是未分派
#             draft_order.write({'state': 'assign', 'user_id': self.env.uid})
#             if draft_order.type == 'out':
#                 return {
#                     'code': '200',
#                     # 'data': data,
#                     'data': {
#                         'trans_type': 'out',
#                         'task_id': draft_order.id,
#                         'location': draft_order.location_id.name,
#                         'user_id': draft_order.qc_user.name,
#                         'plate': draft_order.plate,
#                     }
#                 }
#         res =super(TransMobiel, self).get_trans_task()
#         return res
class StockWeigh(models.Model):
    _inherit = 'stock.weigh'

    #质检换盘时，如果明细都是内部调拨，则生成内部调拨任务
    @api.model
    def change_plate(self):
        plate = self.env['quality.plate'].search([('state', '=', 'draft'), ('user_id', '=', self._context['uid'])])
        if plate and plate.line_ids:
            if all([a.method == 'internal_out' for a in plate.line_ids]):
                internal_trans_obj = self.env['internal.trans.mobile']
                lines = []
                trans_id = plate.line_ids[0].quality_id.sample_trans_id
                trans_order = internal_trans_obj.search([('trans_id', '=', trans_id.id), ('state', '=', 'draft')])
                if not trans_order:
                    trans_order = internal_trans_obj.create({
                        'trans_id': trans_id.id,
                        'location_id': trans_id.location_id.id,
                        'plate': plate.name,
                        'qc_user': plate.user_id.id,
                    })
                for line in plate.line_ids:
                    vals = {
                        'product_id': line.product_id.id,
                        'qty': line.product_qty,
                        'src_location': trans_id.location_id.id,
                        'net_weight': line.net_weight,
                        'gross_weight': line.gross_weight,
                        'sequence': line.sequence,
                        'panwei': '1-' + str(line.sequence),
                        'code': int(line.name),
                    }
                    lines.append((0,0,vals))
                trans_order.write({'line_ids': lines, 'plate': plate.name, 'qc_user': plate.user_id.id,})
            plate.state = 'wait_pick_in'
            obj = self.env['quality.plate'].search([], order="id desc", limit=1)
            name = 1
            if obj:
                name = int(obj.name) + 1
            self.env['quality.plate'].create({
                'user_id': self.env.uid,
                'state': 'draft',
                'name': "%s" % name
            })
            return name
        res = super(StockWeigh, self).change_plate()
        return res
    @api.model
    def split_plate_done(self):
        plate = self.env['quality.plate'].search([('state', '=', 'draft'), ('user_id', '=', self._context['uid'])])
        if plate and plate.line_ids:
            if all([a.method == 'internal_out' for a in plate.line_ids]):
                internal_trans_obj = self.env['internal.trans.mobile']
                lines = []
                trans_id = plate.line_ids[0].quality_id.sample_trans_id
                trans_order = internal_trans_obj.search([('trans_id', '=', trans_id.id), ('state', '=', 'draft')])
                if not trans_order:
                    trans_order = internal_trans_obj.create({
                        'trans_id': trans_id.id,
                        'location_id': trans_id.location_id.id,
                        'plate': plate.name,
                        'qc_user': plate.user_id.id,
                    })
                for line in plate.line_ids:
                    vals = {
                        'product_id': line.product_id.id,
                        'qty': line.product_qty,
                        'src_location': trans_id.location_id.id,
                        'net_weight': line.net_weight,
                        'gross_weight': line.gross_weight,
                        'sequence': line.sequence,
                        'panwei': '1-' + str(line.sequence),
                        'code': int(line.name),
                    }
                    lines.append((0,0,vals))
                trans_order.write({'line_ids': lines, 'qc_user': plate.user_id.id, 'plate': plate.name,})
                plate.state = 'wait_pick_in'
            else:
                res = super(StockWeigh, self).split_plate_done()
                return res