# -*- coding: utf-8 -*-
from openerp import models, api, fields
import math


class MobilePick(models.Model):
    _name= 'batar.mobile.pick'


    PRIORITIES = [('0', 'Not urgent'), ('1', 'Normal'), ('2', 'Urgent'), ('3', 'Very Urgent')]
    name = fields.Char(string='Name', default='/')
    user_id = fields.Many2one('res.users', string='Pick User')
    partner_id = fields.Many2one('res.partner', string='Customer')
    line_ids = fields.One2many('mobile.pick.line', 'pick_id', string='Lines')
    state = fields.Selection([('draft', 'Draft'), ('process', 'process'), ('done', 'Done')], string='State', default='draft')
    tuopan_qty = fields.Float(string='Tuopan Qty')
    # pick_ids = fields.One2many('stock.picking', 'mobile_pick', string='Pick line')
    pick_ids = fields.Many2many('stock.picking', 'mobile_pick', id1='mobile_pick_id', id2='pick_id', string='Picking')
    priority = fields.Selection(PRIORITIES, string='priority', default='2')


    @api.model
    def get_tuopan_type(self):
        '''
        获得所有托盘的类型,后期需要过滤掉没有该类型的托盘数据
        '''
        types = self.env['tuo.pan.type'].search([])
        result = {
            'code':'500',
            'msg':u"没有可用托盘数据，请联系管理员添加",
            'list':[]
        }
        type_list= []
        for type_line in types:
            type_list.append({
                'id':type_line.id,
                'name':type_line.name,
                'code':type_line.code,
            })
        if type_list:
            result['code'] = '200'
            result['msg']= ""
            result['list'] = type_list
        return  result

    @api.model
    def get_pick_task(self):
        result = {
            'code':'500',
            'type':'task',
            'msg':u"当前没有任务,请等待"

        }
        pick_obj = self.env['batar.mobile.pick']
        task = pick_obj.search([('user_id', '=', self.env.uid), ('state', '!=', 'done')],limit=1)
        if not task:
            pick_type_id = self.env['stock.picking.type'].with_context(lang='en').search([('name', 'ilike', 'Pick')],  limit=1).id
            pick_search_list = [('picking_type_id', '=', pick_type_id), ('priority', '=', '3'), ('state', '=', 'assigned'), ('mobile_user', '=', False)]
            pick_p3 = self.env['stock.picking'].search( pick_search_list, limit=1,order='id asc')
            if pick_p3:
                pass
            else:
                pick_search_list = [('picking_type_id', '=', pick_type_id), ('priority', '=', '2'), ('state', '=', 'assigned'), ('mobile_user', '=', False)]
                pick_p2 = self.env['stock.picking'].search(pick_search_list ,limit=1, order='id asc')
                if pick_p2:
                    pass
                else:
                    pick_search_list =[('picking_type_id', '=', pick_type_id), ('priority', 'not in', ['2', '3']), ('state', '=', 'assigned'), ('mobile_user', '=', False)]
                    pick_p = self.env['stock.picking'].search(pick_search_list, limit=1, order='id asc')
                    if pick_p:
                        pass
                    else:
                        #当前没有任务
                        return  result
        else:
            #存在上一次中断的任务
            pass






    @api.model
    def get_next_line(self, line_id):
        """
        下一条任务
        :param  line_id: 当前分拣明细的ID
        """
        line = self.env['mobile.pick.line'].browse([line_id])
        line.write({'state': 'done'})
        next_sequence = line.sequence + 1
        #当前是退货操作，则对应的分拣单OP完成数减去操作数,否则加上当前操作数
        if line.is_return:
            qty = line.operation_id.qty_done - line.qty
        else:
            qty = line.operation_id.qty_done + line.qty
        line.operation_id.write({'qty_done': qty})
        task = line.pick_id
        # lines = task.line_ids.ids
        # line.write({'state': 'done'})
        #检查是否有退货
        return_order = self.env['mobile.pick.line'].search([('is_return', '=', True), ('state', '!=', 'done')])
        if return_order:
            return_order[0].write({'sequence': next_sequence})
            return return_order[0].read(['id', 'default_code', 'qty', 'src_location', 'sequence', 'des_location', 'is_return'])
        else:
            #通过当前ID在明细中的下标查找下一个
            # 当前分拣单中的所有拣货明细（剔除退货明细）
            lines = self.env['mobile.pick.line'].search([('pick_id', '=', line.pick_id.id), ('is_return', '=', False), ('state', '=', 'draft')])
            if lines:
                lines[0].write({'sequence': next_sequence})
                return lines[0].read(['id', 'default_code', 'qty', 'src_location', 'sequence', 'des_location', 'is_return'])
            else:
                task.write({'state': 'done'})
                task.pick_ids.do_new_transfer()
                msg = {}
                msg['title'] = 'Done!'
                msg['qty_done'] = len(lines)
                return [msg]
            # next_index = lines.index(line_id) + 1
            # if next_index < len(lines):
            #     next_id = lines[next_index]
            #     next_line = self.env['mobile.pick.line'].browse([next_id])
            #     return next_line.read(['id', 'default_code', 'qty', 'src_location', 'sequence'])
            # else:
            #     task.write({'state': 'done'})
            #     task.pick_ids.do_new_transfer()
            #     msg = {}
            #     msg['title'] = 'Done!'
            #     msg['qty_done'] = len(lines)
            #     return [msg]

    # @api.model
    # def get_doing_line(self):
    #     """
    #     返回任务，查找单据的未完成明细
    #     """
    #     pick_obj = self.env['batar.mobile.pick']
    #     task = pick_obj.search([('user_id', '=', self.env.uid), ('state', '!=', 'done')])
    #     if task:
    #         for line in task[0].line_ids:
    #             if line.state == 'draft':
    #                 return line.read(['id','default_code', 'qty', 'src_location', 'sequence'])

    @api.model
    def get_pre_line(self, line_id):
        """
        查看上一条任务
        :param  line_id: 当前分拣明细的ID
        """
        line = self.env['mobile.pick.line'].browse([line_id])
        if line.sequence == 1:
            msg = {}
            msg['title'] = 'no data'
            return [msg]
        else:
            pre_sequence = line.seuence - 1
            pre_line = self.env['mobile.pick.line'].search([('sequence', '=', pre_sequence), ('pick_id', '=', line.pick_id.id)])
            return pre_line.read(['id', 'default_code', 'qty', 'src_location', 'des_location', 'sequence'])
        # task = line.pick_id
        # lines = task.line_ids.ids
        # pre_index = lines.index(line_id) - 1
        # if pre_index >= 0:
        #     pre_id = lines[pre_index]
        #     pre_line = self.env['mobile.pick.line'].browse([pre_id])
        #     return pre_line.read(['id', 'default_code', 'qty', 'src_location', 'sequence'])
        # else:
        #     msg = {}
        #     msg['title'] = 'no data'
        #     return [msg]

    @api.model
    def get_priority_task(self,pick_obj,pick):
        lines = []
        pick_lines = []
        order_value = {
            'name': self.env['ir.sequence'].next_by_code('mobile_pick') or '/',
            'user_id': self.env.uid,
            'partner_id': pick[0].partner_id.id,
            'state': 'draft',
        }
        pick_task = pick_obj.create(order_value)
        volume = 0
        todo_product = []
        t_volume = 60.0
        p_volume = 1.0
        # sequence = 0
        tuopan = 1
        gezi = 1
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
                }
                # 根据明细行总容量，及分拣的托盘的格子容量，判断是否要拆分
                volume += line.product_qty * line.product_id.product_volume
                todo_product.append(
                    (line.product_id.id, line.product_qty, line.product_qty * line.product_id.product_volume))
                qty = int(p_volume / line.product_id.product_volume)
                todo_qty = line.product_qty
                while todo_qty > 0:
                    vals['qty'] = qty
                    vals['des_location'] = str(tuopan) + '-' + str(gezi)
                    # sequence += 1
                    # vals['sequence'] = sequence
                    pick_task.write({
                        'line_ids': [(0, 0, vals)],
                    })
                    gezi += 1
                    if gezi > 60:
                        tuopan += 1
                        gezi = 1
                    # lines.append((0, 0, vals))
                    todo_qty -= qty
                vals['qty'] = todo_qty
                vals['des_location'] = str(tuopan) + '-' + str(gezi)
                gezi += 1
                if gezi > 60:
                    tuopan += 1
                    gezi = 1
                # sequence += 1
                # vals['sequence'] = sequence
                pick_task.write({
                    'line_ids': [(0, 0, vals)],
                })
            tuopan_qty = math.ceil(volume / t_volume)
            pick_task.write({
                'tuopan_qty': tuopan_qty,
                'pick_ids': [(4, pick[0].id)],
            })
            # order_value['tuopan_qty'] = tuopan_qty
            # order_value['line_ids'] = lines
            # pick_lines.append((4, pick[0].id))
            # order_value['pick_ids'] = pick_lines
            # pick_task = pick_obj.create(order_value)
            pick_task.line_ids[0].write({'sequence': 1})
            return pick_task.line_ids[0].read(['id', 'default_code', 'qty', 'src_location', 'des_location', 'sequence'])
        else:
            pick.write({
                'mobile_user': self.env.uid,
            })
            for line in pick:
                for op in line.pack_operation_product_ids:
                    vals = {
                        'product_id': op.product_id.id,
                        'src_location': op.location_id.id,
                        'state': 'draft',
                        'operation_id': op.id,
                    }
                    volume += op.product_qty * op.product_id.product_volume
                    todo_product.append(
                        (op.product_id.id, op.product_qty, op.product_qty * op.product_id.product_volume))
                    qty = int(p_volume / op.product_id.product_volume)
                    todo_qty = op.product_qty
                    while todo_qty > qty:
                        vals['qty'] = qty
                        vals['des_location'] = str(tuopan) + '-' + str(gezi)
                        # sequence += 1
                        # vals['sequence'] = sequence
                        pick_task.write({
                            'line_ids': [(0, 0, vals)],
                        })
                        gezi += 1
                        if gezi > 60:
                            tuopan += 1
                            gezi = 1
                        # lines.append((0, 0, vals))
                        todo_qty -= qty
                    vals['qty'] = todo_qty
                    vals['des_location'] = str(tuopan) + '-' + str(gezi)
                    gezi += 1
                    if gezi > 60:
                        tuopan += 1
                        gezi = 1
                    # sequence += 1
                    # vals['sequence'] = sequence
                    pick_task.write({
                        'line_ids': [(0, 0, vals)],
                    })
                pick_lines.append((4, line.id))
            tuopan_qty = math.ceil(volume / t_volume)
            pick_task.write({
                'tuopan_qty': tuopan_qty,
                'pick_ids': pick_lines,
            })
            # order_value['tuopan_qty'] = tuopan_qty
            # order_value['line_ids'] = lines
            # order_value['pick_ids'] = pick_lines
            # pick_task = pick_obj.create(order_value)
            pick_task.line_ids[0].write({'sequence': 1})
            return pick_task.line_ids[0].read(['id', 'default_code', 'qty', 'src_location', 'des_location', 'sequence'])

    @api.model
    def get_pick_task(self,type_id=None):
        """
        同一个级别的分拣任务只能是一个
        分拣员登录系统后，获取分拣任务
        :param  p_volume: 分拣盘的单格容量
        :param  t_volume: 分拣盘的总容量
        """
        result = {
            'code':'500',
            'type':'task',
            'msg':u"获得任务失败",
            'task':{}
        }
        pick_obj = self.env['batar.mobile.pick']
        task = pick_obj.search([('user_id', '=', self.env.uid), ('state', '!=', 'done')])


        if task:
            #获得一条待退货信息
            return_order = self.env['mobile.pick.line'].search([('pick_id', '=', task.id), ('is_return', '=', True), ('state', '=', 'draft')],limit=1)
            #检查是否有未完成的退货单，有则优先。
            if return_order:
                if not return_order.sequence:
                    sequence = task.line_ids.sequence + 1
                    return_order.write({'sequence': sequence})
                return return_order.read(['id','default_code', 'qty', 'src_location', 'des_location', 'sequence'])
            else:
                todo_order = self.env['mobile.pick.line'].search([('pick_id', '=', task.id), ('is_return', '=', False), ('state', '=', 'draft')])
                if not todo_order[0].sequence:
                    sequence = task.line_ids[0].sequence + 1
                    todo_order[0].write({'sequence': sequence})
                return todo_order[0].read(['id','default_code', 'qty', 'src_location', 'des_location', 'sequence'])
                # for line in task.line_ids:
                #     if line.state == 'draft':
                #         line.write({'sequence': sequence})
                #         return line.read(['id','default_code', 'qty', 'src_location', 'sequence'])
        else:
            tuopan_obj = self.env['batar.pick.tuopan']
            pick_type_id = self.env['stock.picking.type'].with_context(lang='en').search([('name','ilike','Pick')],limit=1).id
            pick_p3 = self.env['stock.picking'].search([('picking_type_id', '=', pick_type_id), ('priority', '=', '3'), ('state', '=', 'assigned'), ('mobile_user', '=', False)], order='id asc')
            pick_p2 = self.env['stock.picking'].search([('picking_type_id', '=', pick_type_id), ('priority', '=', '2'), ('state', '=', 'assigned'), ('mobile_user', '=', False)], order='id asc')
            pick_p = self.env['stock.picking'].search([('picking_type_id', '=', pick_type_id), ('priority', 'not in', ['2', '3']), ('state', '=', 'assigned'), ('mobile_user', '=', False)], order='id asc')
            if pick_p3:
                res = self.get_priority_task(pick_obj,pick_p3)
                return res
            if pick_p2:
                res = self.get_priority_task(pick_obj,pick_p2)
                return res
            if pick_p:
                sample_location = pick_p[0].sample_location
                customer = pick_p[0].partner_id
                domain = [('picking_type_id', '=', pick_type_id), ('priority', 'not in', ['2','3']), ('state', '=', 'assigned'), ('partner_id', '=', customer.id), ('sample_location', '=', sample_location.id), ('mobile_user', '=', False)]
                todo_pick = self.env['stock.picking'].search(domain)
                res = self.get_priority_task(pick_obj,todo_pick)
                return res
            else:
                msg = {}
                msg['title'] = "no picking ids"
                return [msg]

class MobilePickLine(models.Model):
    _name = 'mobile.pick.line'
    _order = 'sequence desc'

    pick_id = fields.Many2one('batar.mobile.pick', string='Pick Order')
    product_id = fields.Many2one('product.product', string='Product')
    default_code = fields.Char(related='product_id.default_code', string='Default Code')
    qty = fields.Integer(string='Qty')
    src_location = fields.Many2one('stock.location', string='Src Location')
    des_location = fields.Char(string='Dest Location')
    sequence = fields.Integer(string='Sequence', default=0)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')])
    operation_id = fields.Many2one('stock.pack.operation', string='Operation')
    is_return = fields.Boolean(string='Rerurn', default=False)

