# -*- coding: utf-8 -*-
from openerp import models, api, fields
import math

class MobilePick(models.Model):
    _name= 'batar.mobile.picking'
    _order = 'id desc'

    name = fields.Char(string='Name', default='/')
    user_id = fields.Many2one('res.users', string='Pick User')
    partner_id = fields.Many2one('res.partner', string='Customer')
    line_ids = fields.One2many('mobile.picking.line', 'pick_id', string='Lines')
    state = fields.Selection([('draft', 'Draft'), ('process', 'process'), ('done', 'Done')], string='State', default='draft')
    pick_ids = fields.Many2many('stock.picking', 'mobile_pick', id1='mobile_picking_id', id2='pick_id', string='Picking')

    @api.model
    def get_task_state(self, line_id):
        line = self.env['mobile.picking.line'].browse([line_id])
        task = line.pick_id
        if task.state == 'done':
            return True
        else:
            return False

    @api.multi
    @api.onchange('line_ids')
    def onchange_state(self):
        if self.line_ids:
            state = set([x.state for x in self.line_ids])
            if list(state) == ['delivery']:
                self.write({'state': 'done'})

    @api.model
    def change_tuopan(self, line_id):
        """
        更换新托盘
        """
        line = self.env['mobile.picking.line'].browse([line_id])
        p, g = line.des_location.split('-')
        new_location = str(int(p) + 1) + '-' + '1'
        # 原有退货任务同时更新托盘位置
        return_lines = self.env['mobile.picking.line'].search([('pick_id', '=', line.pick_id.id), ('des_location', '=', line.des_location), ('is_return', '=', True), ('state', '=', 'draft')])
        line.write({'des_location': new_location})
        return_lines.write({'des_location': new_location})
        data = line.read(['id', 'default_code', 'qty', 'src_location', 'sequence', 'des_location', 'is_return'])
        result = {
            'code': '200',
            'data': dict(data[0]),
        }
        result['data']['product'] = line.product_id.name
        return result

    @api.model
    def get_next_line(self, line_id, done_qty):
        """
        下一条任务
        :param  line_id: 当前分拣明细的ID
        """
        result = {
            'code': '500',
            'data': {},
        }
        line = self.env['mobile.picking.line'].browse([line_id])
        next_sequence = line.sequence + 1
        p, g = line.des_location.split('-')
        next_des_location = p + '-' + str(int(g) + 1)
        # 当前是退货操作，则对应的分拣单OP完成数减去操作数,否则加上当前操作数
        if line.is_return:
            qty = line.operation_id.qty_done - line.qty
        else:
            qty = line.operation_id.qty_done + done_qty
        line.operation_id.write({'qty_done': qty})
        task = line.pick_id
        #
        # # 检查是否有退货
        # return_order = self.env['mobile.picking.line'].search([('is_return', '=', True), ('state', '!=', 'done'), ('pick_id', '=', task.id)])
        # if return_order:
        #     return_order[0].write({'sequence': next_sequence})
        #     data = return_order[0].read(['id', 'default_code', 'qty', 'src_location', 'sequence', 'des_location', 'is_return'])
        #     result['code'] = '300'
        #     result['data'] = dict(data[0])
        #     result['data']['product'] = return_order[0].product_id.name
        #     return result
        # else:
        # 通过当前ID在明细中的下标查找下一个
        # 当前分拣单中的所有拣货明细（剔除退货明细）
        if done_qty == 0:
            line.write({'des_location': next_des_location, 'state': 'process'})
            data = line.read(['id', 'default_code', 'qty', 'src_location', 'sequence', 'des_location', 'is_return'])
            result['code'] = '201'
            result['data'] = dict(data[0])
            result['data']['product'] = line.product_id.name
            return result
        if done_qty == line.qty:
            line.write({'state': 'done'})
            # 检查是否有退货
            return_order = self.env['mobile.picking.line'].search(
                [('is_return', '=', True), ('state', '!=', 'done'), ('pick_id', '=', task.id)])
            if return_order:
                return_order[0].write({'sequence': next_sequence, 'state': 'process'})
                data = return_order[0].read(
                    ['id', 'default_code', 'qty', 'src_location', 'sequence', 'des_location', 'is_return'])
                result['code'] = '300'
                result['data'] = dict(data[0])
                result['data']['product'] = return_order[0].product_id.name
                return result
            else:
                lines = self.env['mobile.picking.line'].search(
                    [('pick_id', '=', line.pick_id.id), ('is_return', '=', False), ('state', '=', 'draft'), ('product_id', '=', line.product_id.id)])
                if lines:
                    lines[0].write({'sequence': next_sequence, 'des_location': line.des_location, 'state': 'process'})
                    data = lines[0].read(['id', 'default_code', 'qty', 'src_location', 'sequence', 'des_location', 'is_return'])
                    result['code'] = '201'
                    result['data'] = dict(data[0])
                    result['data']['product'] = lines[0].product_id.name
                    return result
                lines_p = self.env['mobile.picking.line'].search([('pick_id', '=', line.pick_id.id), ('is_return', '=', False), ('state', '=', 'draft')])
                if lines_p:
                    lines_p[0].write({'sequence': next_sequence, 'des_location': next_des_location, 'state': 'process'})
                    data = lines_p[0].read(['id', 'default_code', 'qty', 'src_location', 'sequence', 'des_location', 'is_return'])
                    result['code'] = '201'
                    result['data'] = dict(data[0])
                    result['data']['product'] = lines_p[0].product_id.name
                    return result
                else:
                    task.write({'state': 'process'})
                    lines = self.env['mobile.picking.line'].search([('pick_id', '=', task.id), ('is_return', '=', False)])
                    lines_r = self.env['mobile.picking.line'].search([('pick_id', '=', task.id), ('is_return', '=', True)])
                    for x in lines:
                        x_return = sum(y.qty for y in lines_r if y.src_location == x.src_location and y.product_id == x.product_id)
                        if x.qty == x_return:
                            return_ids = self.env['mobile.picking.line'].search([('pick_id', '=', task.id), ('is_return', '=', True), ('src_location', '=', x.src_location.id), ('product_id', '=', x.product_id.id)])
                            x.write({'state': 'delivery'})
                            return_ids.write({'state': 'delivery'})
                    pick_total = sum(x.qty for x in task.line_ids if not x.is_return)
                    return_total = sum(x.qty for x in task.line_ids if x.is_return)
                    result['code'] = '400'
                    result['data']['total'] = pick_total - return_total
                    for x in task.pick_ids:
                        return_pick = sum(y.qty_return for y in x.pack_operation_product_ids)
                        if return_pick > 0:
                            backorder_wiz_id = x.do_new_transfer()['res_id']
                            backorder_wiz = self.env['stock.backorder.confirmation'].browse([backorder_wiz_id])
                            backorder_wiz.process_cancel_backorder()
                        else:
                            x.do_new_transfer()
                    # if return_total > 0:
                    #     backorder_wiz_id = task.pick_ids.do_new_transfer()['res_id']
                    #     backorder_wiz = self.env['stock.backorder.confirmation'].browse([backorder_wiz_id])
                    #     backorder_wiz.process_cancel_backorder()
                    # else:
                    #     task.pick_ids.do_new_transfer()
                    return result
        elif done_qty < line.qty:
            new_sequence = line.sequence + 1
            new_line = line.copy({'qty': line.qty - done_qty, 'state': 'process', 'sequence': new_sequence, 'des_location': next_des_location})
            line.write({
                'qty': done_qty,
                'state': 'done',
            })
            result['code'] = '201'
            data = new_line.read(['id', 'default_code', 'qty', 'src_location', 'sequence', 'des_location', 'is_return'])
            result['data'] = dict(data[0])
            result['data']['product'] = new_line.product_id.name
            # 原有退货任务需要根据拆分数量更新托盘位置
            return_line = self.env['mobile.picking.line'].search([('pick_id', '=', task.id), ('des_location', '=', line.des_location), ('is_return', '=', True), ('state', '=', 'draft')], limit=1)
            if return_line.qty > line.qty:
                return_line.copy({'qty': return_line.qty - line.qty, 'des_location': next_des_location})
                return_line.write({'qty': line.qty})
            return result
        else:
            return result

    @api.model
    def get_pre_line(self, line_id):
        """
        查看上一条任务
        :param  line_id: 当前分拣明细的ID
        """
        result = {
            'code': '500',
            'data': {},
        }
        line = self.env['mobile.picking.line'].browse([line_id])
        if line.sequence == 1:
            return result
        else:
            pre_sequence = line.sequence - 1
            pre_line = self.env['mobile.picking.line'].search(
                [('sequence', '=', pre_sequence), ('pick_id', '=', line.pick_id.id)])
            data = pre_line.read(['id', 'default_code', 'qty', 'src_location', 'des_location', 'sequence', 'is_return'])
            result['code'] = '201'
            if pre_line.is_return:
                result['code'] = '300'
            result['data'] = dict(data[0])
            result['data']['product'] = pre_line.product_id.name
            return result

    @api.model
    def get_priority_task(self, pick):
        result = {
            'code': '500',
            'data': {},
        }
        pick_obj = self.env['batar.mobile.picking']
        order_value = {
            'name': self.env['ir.sequence'].next_by_code('mobile_pick') or '/',
            'user_id': self.env.uid,
            'partner_id': pick[0].partner_id.id,
            'state': 'draft',
        }
        pick_task = pick_obj.create(order_value)
        if pick[0].priority in ['2', '3']:
            pick[0].write({
                'mobile_user': self.env.uid,
            })
            for line in pick[0].pack_operation_product_ids:
                vals = {
                    'product_id': line.product_id.id,
                    'src_location': line.location_id.id,
                    'state': 'draft',
                    'operation_id': line.id,
                    # 'qty': line.product_qty,
                    'qty': line.product_qty - line.qty_return,
                }
                pick_task.write({
                    'line_ids': [(0, 0, vals)],
                })
            pick_task.write({
                'pick_ids': [(4, pick[0].id)],
            })
            pick_task.line_ids[0].write({'sequence': 1, 'des_location': '1-1', 'state': 'process'})
            result['code'] = '200'
            data = pick_task.line_ids[0].read(['id', 'default_code', 'qty', 'src_location', 'des_location', 'sequence', 'is_return'])
            result['data'] = dict(data[0])
            result['data']['product'] = pick_task.line_ids[0].product_id.name
            return result
        else:
            pick.write({
                'mobile_user': self.env.uid,
            })
            for line in pick:
                for op in line.pack_operation_product_ids:
                    if op.product_qty > op.qty_return:
                        vals = {
                            'product_id': op.product_id.id,
                            'src_location': op.location_id.id,
                            'state': 'draft',
                            'operation_id': op.id,
                            # 'qty': op.product_qty,
                            'qty': op.product_qty - op.qty_return,
                        }
                        pick_task.write({
                            'line_ids': [(0, 0, vals)],
                        })
                pick_task.write({
                    'pick_ids': [(4, line.id)],
                })
            if pick_task.line_ids:
                pick_task.line_ids[0].write({'sequence': 1, 'des_location': '1-1', 'state': 'process'})
                result['code'] = '200'
                data = pick_task.line_ids[0].read(['id', 'default_code', 'qty', 'src_location', 'des_location', 'sequence', 'is_return'])
                result['data'] = dict(data[0])
                result['data']['product'] = pick_task.line_ids[0].product_id.name
                return result
            else:
                # 手机分拣前所有明细都需要全部退货，待后期确认逻辑
                pass

    @api.model
    def get_pick_task(self):
        """
        同一个级别的分拣任务只能是一个
        分拣员登录系统后，获取分拣任务
        :param  p_volume: 分拣盘的单格容量
        :param  t_volume: 分拣盘的总容量
        code: 500  获取任务失败
        code: 200  已新建分拣单并获取当前第一条任务
        code: 201  已获取当前分拣任务
        code：300  已获取退货任务
        code: 400  已完成分拣任务
        """
        result = {
            'code': '500',
            'data': {},
        }
        pick_obj = self.env['batar.mobile.picking']
        task = pick_obj.search([('user_id', '=', self.env.uid), ('state', '!=', 'done')])

        if task:
            if task.state == 'draft' and task.line_ids:
                result['code'] = '201'
                # 如果有未完成的拣货，且已经分配sequence，则返回此分拣任务
                # if task.line_ids[0].sequence != 0 and task.line_ids[0].state == 'draft':
                if task.line_ids[0].state == 'process':
                    if task.line_ids[0].is_return:
                        result['code'] = '300'
                    data = task.line_ids[0].read(['id', 'default_code', 'qty', 'src_location', 'des_location', 'sequence', 'is_return'])
                    result['data'] = dict(data[0])
                    result['data']['product'] = task.line_ids[0].product_id.name
                    return result
                # 获得一条待退货信息
                # return_order = self.env['mobile.picking.line'].search([('pick_id', '=', task.id), ('is_return', '=', True), ('state', '=', 'draft')], limit=1)
                return_order = self.env['mobile.picking.line'].search(
                    [('pick_id', '=', task.id), ('is_return', '=', True), ('state', '!=', 'done')], limit=1)
                # 检查是否有未完成的退货单，有则优先。
                if return_order:
                    if not return_order.sequence:
                        sequence = task.line_ids[0].sequence + 1
                        return_order.write({'sequence': sequence})
                    result['code'] = '300'
                    data = return_order.read(['id', 'default_code', 'qty', 'src_location', 'des_location', 'sequence', 'is_return'])
                    result['data'] = dict(data[0])
                    result['data']['product'] = return_order.product_id.name
                    return result
                else:
                    # todo_order = self.env['mobile.picking.line'].search(
                    #     [('pick_id', '=', task.id), ('is_return', '=', False), ('state', '=', 'draft')])
                    todo_order = self.env['mobile.picking.line'].search(
                         [('pick_id', '=', task.id), ('is_return', '=', False), ('state', '!=', 'done')])
                    if not todo_order[0].sequence:
                        sequence = task.line_ids[0].sequence + 1
                        todo_order[0].write({'sequence': sequence})
                    # result['code'] = '201'
                    data = todo_order[0].read(['id', 'default_code', 'qty', 'src_location', 'des_location', 'sequence', 'is_return'])
                    result['data'] = dict(data[0])
                    result['data']['product'] = todo_order[0].product_id.name
                    return result
            else:
                result['code'] = '400'
                pick_total = sum(x.qty for x in task.line_ids if not x.is_return)
                return_total = sum(x.qty for x in task.line_ids if x.is_return)
                data = task.line_ids[0].read(['id', 'default_code', 'qty', 'src_location', 'des_location', 'sequence', 'is_return'])
                result['data'] = dict(data[0])
                result['data']['product'] = task.line_ids[0].product_id.name
                result['data']['total'] = pick_total - return_total
                return result

        else:
            pick_type_id = self.env['stock.picking.type'].with_context(lang='en').search([('name', 'ilike', 'Pick')],
                                                                                         limit=1).id
            pick_p3 = self.env['stock.picking'].search(
                [('picking_type_id', '=', pick_type_id), ('priority', '=', '3'), ('state', '=', 'assigned'),
                 ('mobile_user', '=', False)], order='id asc')
            pick_p2 = self.env['stock.picking'].search(
                [('picking_type_id', '=', pick_type_id), ('priority', '=', '2'), ('state', '=', 'assigned'),
                 ('mobile_user', '=', False)], order='id asc')
            pick_p = self.env['stock.picking'].search(
                [('picking_type_id', '=', pick_type_id), ('priority', 'not in', ['2', '3']), ('state', '=', 'assigned'),
                 ('mobile_user', '=', False)], order='id asc')
            if pick_p3:
                print 'p3'
                res = self.get_priority_task(pick_p3)
                return res
            if pick_p2:
                print 'p2'
                res = self.get_priority_task(pick_p2)
                return res
            if pick_p:
                print 'p'
                sample_location = pick_p[0].sample_location
                customer = pick_p[0].partner_id
                domain = [('picking_type_id', '=', pick_type_id), ('priority', 'not in', ['2', '3']),
                          ('state', '=', 'assigned'), ('partner_id', '=', customer.id),
                          ('sample_location', '=', sample_location.id), ('mobile_user', '=', False)]
                todo_pick = self.env['stock.picking'].search(domain)
                res = self.get_priority_task(todo_pick)
                return res
            else:
                result['code'] = '500'
                return result

class MobilePickLine(models.Model):
    _name = 'mobile.picking.line'
    _order = 'sequence desc'

    pick_id = fields.Many2one('batar.mobile.picking', string='Pick Order', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    default_code = fields.Char(related='product_id.default_code', string='Default Code')
    qty = fields.Integer(string='Qty')
    src_location = fields.Many2one('stock.location', string='Src Location')
    des_location = fields.Char(string='Dest Location')
    sequence = fields.Integer(string='Sequence', default=0)
    state = fields.Selection([('draft', 'Draft'), ('process', 'Process'), ('done', 'Done'), ('delivery', 'Delivery')])
    operation_id = fields.Many2one('stock.pack.operation', string='Operation')
    is_return = fields.Boolean(string='Rerurn', default=False)
