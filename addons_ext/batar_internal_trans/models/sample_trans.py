# -*- coding: utf-8 -*-
from openerp import api, fields, models, exceptions
from lxml import etree

class Picking(models.Model):
    _inherit = 'stock.picking'

    sample_trans_id = fields.Many2one('batar.sample.trans', string='Sample Trans')

class SampleTrans(models.Model):
    _name = 'batar.sample.trans'
    _inherit = ['ir.needaction_mixin']

    name = fields.Char(string='Name', default='/', readonly=True)
    type = fields.Selection([('in', 'In'), ('out', 'Out')], string='Trans Type', states={'draft': [('readonly', False)]}, readonly=True, default='in')
    ref = fields.Char(string='Ref', readonly=True)
    line_ids = fields.One2many('sample.trans.lines', 'trans_id', string='Trans Lines', states={'process': [('readonly', False)]}, readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('process', 'Process'), ('confirm', 'Confirm'), ('done', 'Done'), ('cancel', 'Cancel')], default='draft')
    order_type = fields.Selection([('source_doc', 'Source Doc'), ('review_doc', 'Review Doc')], default='source_doc')
    location_id = fields.Many2one('stock.location', string='Location', states={'draft': [('readonly', False)]}, readonly=True, required=True)
    picking_ids = fields.One2many('stock.picking', 'sample_trans_id', string='Picking')
    picking_counts = fields.Integer(string='Counts of Picking', compute='_compute_picking_counts')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    shenhe_user = fields.Many2one('res.users', string='ShenHe User')

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['process', 'draft'])]

    @api.multi
    @api.depends('picking_ids')
    def _compute_picking_counts(self):
        self.ensure_one()
        self.picking_counts = len(self.picking_ids)

    @api.multi
    def add_product(self):
        #弹出手动选择 或 样品推荐页面
        self.ensure_one()
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sample.trans.wizard',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('batar_internal_trans.internal_trans_wizard_form_view').id,
            'target': 'new',
        }

    @api.multi
    def action_view_picking(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all')
        result = {
            'name': action.name,
            'type': action.type,
            'view_mode': action.view_mode,
            'view_type': action.view_type,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        picking_ids = self.picking_ids.ids
        #一条记录则打开form视图，多条记录打开tree视图
        if len(picking_ids) == 1:
            form = self.env.ref('stock.view_picking_form', False)
            form_id = form.id if form else False
            result['views'] = [(form_id, 'form')]
            result['res_id'] = picking_ids[0]
        elif len(picking_ids) > 1:
            result['domain'] = [('id', 'in', picking_ids)]
        return result


    @api.model
    def create(self, vals):
        if vals.get('name', '/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sample_trans') or '/'
        res = super(SampleTrans, self).create(vals)
        return res

    @api.multi
    def action_process(self):
        #制单人提交移库单
        self.ensure_one()
        if self.line_ids:
            return self.write({'state': 'process'})
        else:
            raise exceptions.ValidationError(u'不能提交空单据')
    @api.multi
    def action_cancel(self):
        #审核不通过
        self.ensure_one()
        self.line_ids.write({'is_pass': False})
        return self.write({'state': 'cancel', 'shenhe_user': self.env.uid})

    @api.multi
    def action_part_confirm(self):
        #审批人部分通过
        self.write({'state': 'confirm', 'shenhe_user': self.env.uid})
        pick_obj = self.env['stock.picking']
        data_obj = self.pool['ir.model.data']
        picking_type_id = self.env['stock.picking.type'].with_context(lang='en').search(
            [('name', 'ilike', 'Internal Transfers')], limit=1)
        lines = self.line_ids.filtered(lambda r: r.is_pass == True)
        if self.type == 'in':
            # 样品调入
            res = {}
            # for line in self.line_ids:
            for line in lines:
                move_vals = {
                    'product_id': line.product_id.id,
                    'location_id': line.src_location.id,
                    'location_dest_id': self.location_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uom_qty': line.qty,
                    'name': 'INV:samplemove',
                    'origin': 'SAMPLE:' + self.name
                }
                # 相同源库位的产品放在同一张调拨单
                if line.src_location.id not in res.keys():
                    vals = {
                        'location_id': line.src_location.id,
                        'location_dest_id': self.location_id.id,
                        'picking_type_id': picking_type_id.id,
                        'move_lines': [(0, 0, move_vals)],
                        'sample_trans_id': self.id,
                    }
                    internal_order = pick_obj.create(vals)
                    res[line.src_location.id] = internal_order.id
                else:
                    pick_obj.browse(res[line.src_location.id]).write({'move_lines_related': [(0, 0, move_vals)]})
            pick_obj.browse(res.values()).action_confirm()
            pick_obj.browse(res.values()).action_assign()

        # if self.type == 'out':
        #     #样品调出，则审批后，直接生成分拣任务。
        #     task_vals = {
        #         'trans_id': self.id,
        #         'location_id': self.location_id.id,
        #     }
        #     res = self.env['internal.trans.mobile'].create(task_vals)
        #     #根据明细行生成手机分拣任务的明细，目标库位待定。
        #     trans_lines = []
        #     for line in lines:
        #         line_vals = {
        #             'product_id': line.product_id.id,
        #             'order_id': res.id,
        #             'src_location': self.location_id.id,
        #             'net_weight': line.net_weight,
        #             'qty': line.qty,
        #         }
        #         trans_lines.append((0,0,line_vals))
        #     res.write({'line_ids': trans_lines})
        return True
    @api.multi
    def action_confirm(self):
        #审批人审批订单,全部通过
        # self.write({'state': 'confirm'})
        self.line_ids.write({'is_pass': True})
        return self.action_part_confirm()

    @api.model
    def fields_view_get(self, view_id=None, view_type='tree', toolbar=False, submenu=False):
        res = super(SampleTrans, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if self._context.get('state'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='is_pass']"):
                if self._context.get('type') == 'draft':
                    node.set('invisible', '1')
            res['arch'] = etree.tostring(doc)
        return res
        # pick_obj = self.env['stock.picking']
        # data_obj = self.pool['ir.model.data']
        # picking_type_id = self.env['stock.picking.type'].with_context(lang='en').search([('name', 'ilike', 'Internal Transfers')], limit=1)
        # lines = self.line_ids.filtered(lambda r: r.is_pass == True)
        # if self.type == 'in':
        #     #样品调入
        #     res = {}
        #     # for line in self.line_ids:
        #     for line in lines:
        #         move_vals = {
        #             'product_id': line.product_id.id,
        #             'location_id': line.src_location.id,
        #             'location_dest_id': self.location_id.id,
        #             'product_uom': line.product_id.uom_id.id,
        #             'product_uom_qty': line.qty,
        #             'name': 'INV:samplemove',
        #             'origin': 'SAMPLE:' + self.name
        #         }
        #         #相同源库位的产品放在同一张调拨单
        #         if line.src_location.id not in res.keys():
        #             vals = {
        #                 'location_id': line.src_location.id,
        #                 'location_dest_id': self.location_id.id,
        #                 'picking_type_id': picking_type_id.id,
        #                 'move_lines': [(0,0,move_vals)],
        #                 'sample_trans_id': self.id,
        #             }
        #             internal_order = pick_obj.create(vals)
        #             res[line.src_location.id] = internal_order.id
        #         else:
        #             pick_obj.browse(res[line.src_location.id]).write({'move_lines_related': [(0,0,move_vals)]})
        #     pick_obj.browse(res.values()).action_confirm()
        #     pick_obj.browse(res.values()).action_assign()
        #
        # if self.type == 'out':
        #     #样品调出
        #     res = {}
        #     # for line in self.line_ids:
        #     for line in lines:
        #         move_vals = {
        #             'product_id': line.product_id.id,
        #             'location_id': line.src_location.id,
        #             'location_dest_id': self.location_id.id,
        #             'product_uom': line.product_id.uom_id.id,
        #             'product_uom_qty': line.qty,
        #             'name': 'INV:samplemove',
        #             'origin': 'SAMPLE:' + self.name
        #         }
        #         #相同源库位的产品放在同一张调拨单
        #         if line.dest_location.id not in res.keys():
        #             vals = {
        #                 'location_id': self.location_id.id,
        #                 'location_dest_id': line.dest_location.id,
        #                 'picking_type_id': picking_type_id.id,
        #                 'move_lines_related': [(0,0,move_vals)],
        #                 'sample_trans_id': self.id,
        #             }
        #             internal_order =pick_obj.create(vals)
        #             res[line.dest_location.id] = internal_order.id
        #         else:
        #             pick_obj.browse(res[line.dest_location.id]).write({'move_lines_related': [(0,0,move_vals)]})
        #     pick_obj.browse(res.values()).action_confirm()
        #     pick_obj.browse(res.values()).action_assign()

class TransLines(models.Model):
    _name = 'sample.trans.lines'

    trans_id = fields.Many2one('batar.sample.trans', string='Trans Order')
    product_id = fields.Many2one('product.product', string='Product', states={'draft': [('readonly', False)]}, readonly=True)
    dest_location = fields.Many2one('stock.location', string='Destination Location', states={'draft': [('readonly', False)]}, readonly=True)
    src_location = fields.Many2one('stock.location', string='Source Location', states={'draft': [('readonly', False)]}, readonly=True)
    type = fields.Selection([('in', 'In'), ('out', 'Out')], string='Type')
    qty = fields.Float(string='Qty', states={'draft': [('readonly', False)]}, readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('process', 'Process'), ('confirm', 'Confirm'), ('done', 'Done'), ('cancel', 'Cancel')],
                             related='trans_id.state', readonly=True, store=True, default='draft')
    is_pass = fields.Boolean(string='Pass', default=True, states={'draft': [('readonly', False)], 'process': [('readonly', False)]}, readonly=True)

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='tree', toolbar=False, submenu=False):
    #     res = super(TransLines, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if self._context.get('state'):
    #         doc = etree.XML(res['arch'])
    #         for node in doc.xpath("//field[@name='is_pass']"):
    #             if self._context.get('type') == 'draft':
    #                 node.set('invisible', '1')
    #         res['arch'] = etree.tostring(doc)
    #     return res