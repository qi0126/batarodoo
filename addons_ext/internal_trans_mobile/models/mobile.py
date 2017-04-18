# -*- coding: utf-8 -*-
from openerp import api, fields, models, exceptions
import openerp.addons.decimal_precision as dp
class TransMobile(models.Model):
    _name = 'internal.trans.mobile'

    user_id = fields.Many2one('res.users', string='User', readonly=True)
    name = fields.Char(string='Name', default='/', readonly=True)
    trans_id = fields.Many2one('batar.sample.trans', string='Trans', readonly=True)
    line_ids = fields.One2many('trans.mobile.lines', 'order_id', string='Lines', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('assign', 'Assign'), ('tag', 'Tag'), ('done', 'Done')], string='State', default='draft')
    location_id = fields.Many2one('stock.location', related='trans_id.location_id')
    type = fields.Selection(related='trans_id.type', store=True,readonly=True)
    qc_user = fields.Many2one('res.users', string='QC', readonly=True)
    plate = fields.Char(string='Plate name')
    @api.model
    def create(self, vals):
        if vals.get('name', '/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('trans_mobile') or '/'
        res = super(TransMobile, self).create(vals)
        return res
    def get_line_value(self, line):
        return {
            'id': line.id,
            'product': line.product_id.name,
            'default_code': line.product_id.default_code,
            'qty': line.qty,
            'src_location': line.src_location.name,
            'dest_location': line.dest_location.name,
            'sequence': line.sequence,
            'uom': line.uom_id.name,
            'state': line.state,
            'panwei': line.panwei,
        }
    @api.multi
    def delivery(self):
        #分拣完后交货至验货区，打标签
        if all([a.state == 'done' for a in self.line_ids]):
            return self.write({'state': 'tag'})
        else:
            raise exceptions.ValidationError(u'所有明细必须完成!')
    @api.multi
    def confirm_tag(self):
        #标签完之后，完成入样品库
        self.ensure_one()
        if self.state == 'tag':
            self.write({'state': 'done'})
            self.trans_id.picking_ids.do_new_transfer()
            self.trans_id.write({'state': 'done'})
        return self.line_ids.print_product_tag()

    @api.model
    def get_trans_task(self):
        trans_obj = self.env['internal.trans.mobile']
        assign_order = trans_obj.search([('state', 'in', ['assign', 'tag']), ('user_id', '=', self.env.uid)], limit=1)
        draft_order = trans_obj.search([('state', '=', 'draft')], limit=1)
        if assign_order:
            #已经分配调拨任务
            process_task = assign_order.line_ids.filtered(lambda r: r.state == 'process')
            if all([a.state == 'draft' for a in assign_order.line_ids]):
                return {
                    'code': '200',
                    'data': {
                        'trans_type': 'out',
                        'task_id': assign_order.id,
                        'location': assign_order.location_id.name,
                        'plate': assign_order.plate,
                        'user_id': assign_order.qc_user.name,
                    }
                }
            if process_task:
                data = self.get_line_value(process_task)
                if assign_order.trans_id.type == 'in':
                    data['trans_type'] = 'in'
                else:
                    data['trans_type'] = 'out'
                return {'code': '201', 'data': data}
            else:
                data = self.get_line_value(assign_order.line_ids[-1])
                total = sum([x.qty for x in assign_order.line_ids])
                data['total'] = total
                if assign_order.trans_id.type == 'in':
                    data['trans_type'] = 'in'
                else:
                    data['trans_type'] = 'out'
                return {'code': '400', 'data': data}
        if draft_order and draft_order.line_ids:
            #存在任务，但是未分派
            draft_order.write({'state': 'assign', 'user_id': self.env.uid})
            #存储库调入样品库，则返回第一条的明细
            if draft_order.type == 'in':
                draft_order.line_ids[0].write({'state': 'process', 'sequence': 1, 'panwei': '1-1'})
                data = self.get_line_value(draft_order.line_ids[0])
                data['trans_type'] = 'in'
                return {'code': '200', 'data': data,}
            #样品库调出到存储库，则返回需要领取的所有物品明细,任务ID及柜台
            else:
                # data = []
                # for line in draft_order.line_ids:
                #     vals = {
                #         'id': line.id,
                #         'sample_code': line.code,
                #         'default_code': line.product_id.default_code,
                #         'product': line.product_id.name,
                #         'panwei': line.panwei,
                #         'sequence': line.sequence,
                #     }
                #     data.append(vals)
                return {
                    'code': '200',
                    # 'data': data,
                    'data': {
                        'trans_type': 'out',
                        'task_id': draft_order.id,
                        'location': draft_order.location_id.name,
                        'user_id': draft_order.qc_user.name,
                        'plate': draft_order.plate,
                    },
                }
        else:
            return {'code': '500', 'data': ''}

    @api.model
    def change_plate(self, line_id):
        #换盘操作
        line = self.env['trans.mobile.lines'].browse(line_id)
        pan = line.panwei.split('-')[0]
        panwei = str(int(pan) + 1) + '-1'
        line.write({'panwei': panwei})
        data = self.get_line_value(line)
        return {'code': '201', 'data': data}
    @api.model
    def get_next_line(self, line_id):
        #下一条
        line = self.env['trans.mobile.lines'].browse(line_id)
        line.write({'state': 'done'})
        # qty = line.op_id.qty_done + line.qty
        # line.op_id.write({'qty_done': qty})
        if all([a.state == 'done' for a in line.order_id.line_ids]):
            #所有明细都完成，返回 400
            data = self.get_line_value(line)
            total = sum([x.qty for x in line.order_id.line_ids])
            data['total'] = total
            return {'code': '400', 'data': data}
        else:
            next_line = line.order_id.line_ids.filtered(lambda r: r.state == 'draft')[0]
            wei = line.panwei.split('-')[1]
            panwei = line.panwei.split('-')[0] + '-' + str(int(wei) + 1)
            next_line.write({'state': 'process', 'sequence': line.sequence + 1, 'panwei': panwei})
            data = self.get_line_value(next_line)
            return {'code': '201', 'data': data}
    @api.model
    def get_pre_line(self, line_id):
        #查看上一条
        line = self.env['trans.mobile.lines'].browse([line_id])
        if line.sequence == 1:
            return {'code': '500', 'data': {}}
        else:
            pre_sequence = line.sequence - 1
            pre_line = self.env['trans.mobile.lines'].search([('order_id', '=', line.order_id.id), ('sequence', '=', pre_sequence)])
            data = self.get_line_value(pre_line)
            return {'code': '201', 'data': data}
    @api.model
    def get_state(self, line_id):
        trans_line_obj = self.env['trans.mobile.lines']
        task = trans_line_obj.browse(line_id).order_id
        if task.state == 'done':
            return True
        else:
            return False

class TransLines(models.Model):
    _name = 'trans.mobile.lines'
    # _order = 'sequence desc'
    _order = 'sequence'

    product_id = fields.Many2one('product.product', string='Product')
    order_id = fields.Many2one('internal.trans.mobile', string='Order', ondelete='cascade')
    qty = fields.Float(string='Qty', digits=dp.get_precision('Batar price'))
    uom_id = fields.Many2one(related='product_id.uom_id', string='Uom')
    src_location = fields.Many2one('stock.location', string='Src location')
    dest_location = fields.Many2one('stock.location', string='Dest Location')
    net_weight = fields.Float(string='Net Weight', digits=dp.get_precision('Batar price'))
    gross_weight = fields.Float(string='Gross Weight', digits=dp.get_precision('Batar Price'))
    state = fields.Selection([('draft', 'Draft'), ('process', 'Process'), ('done', 'Done')], string='State', default='draft')
    sequence = fields.Integer(string='Sequence')
    panwei = fields.Char(string='Panwei')
    op_id = fields.Many2one('stock.pack.operation', string='Operation')
    user_id = fields.Many2one(related='order_id.user_id', string='User')

    @api.multi
    def print_product_tag(self):
        return self.env['report'].get_action(self, 'internal_trans_mobile.line_product_tag')

class MobileTask(models.Model):
    _inherit = 'batar.mobile.task'
    @api.model
    def get_task(self):
        res = super(MobileTask, self).get_task()
        if res['code'] == '500' and res['type'] == 'pick':
            trans_obj = self.env['internal.trans.mobile']
            res = trans_obj.get_trans_task()
            res['type'] = 'trans'
        return res