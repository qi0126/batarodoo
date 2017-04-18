# -*- coding: utf-8 -*-
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp

class InputMobile(models.Model):
    _name = 'batar.input.mobile'
    _order = 'id desc'

    name = fields.Char(string='Name', default='/', readonly=True)
    user_id = fields.Many2one('res.users', string='QC', states={'draft': [('readonly', False)]}, readonly=True)
    assign_to =fields.Many2one('res.users', string='Picker', states={'draft': [('readonly', False)]}, readonly=True)
    plate_id = fields.Many2one('quality.plate', string='Tuo Pan', states={'draft': [('readonly', False)]}, readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('assigned', 'Assigned'), ('process', 'Process'), ('done', 'Done')], string='State', default='draft')
    line_ids = fields.One2many('batar.input.line', 'input_id', string='Lines', states={'draft': [('readonly', False)]}, readonly=True)
    # partner_id = fields.Many2one('res.partner', string='Vendor', states={'draft': [('readonly', False)]}, readonly=True)
    move_ids = fields.One2many('stock.move', 'input_id', string='Stock Move', states={'draft': [('readonly', False)]}, readonly=True)

    @api.model
    def create(self, vals):
        #名称自动生成
        if vals.get('name', '/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('input_mobile') or '/'
        res = super(InputMobile, self).create(vals)
        return res

    def move_create(self, line):
        data_obj = self.env['ir.model.data']
        location_obj = self.env['stock.location']
        try:
            supplier_loc = data_obj.get_object_reference('stock', 'stock_location_suppliers')[1]
        except:
            supplier_loc = location_obj.search([('usage', '=', 'supplier')])
            supplier_loc = supplier_loc and supplier_loc[0] or False
        move_vals = {
            'product_id': line.product_id.id,
            'location_id': supplier_loc,
            'location_dest_id': line.location_id.id,
            'product_uom': line.product_id.uom_id.id,
            'product_uom_qty': line.qty,
            'name': 'INV:Mobile',
            'origin': 'IM:' + line.input_id.name,
            'net_weight': line.net_weight,
        }
        line.input_id.write({'move_ids': [(0,0,move_vals)]})
        return True

    def get_line_data(self, line):
        result = {
            'code': '201',
            'data': {
                'id': line.id,
                'product': line.product_id.name,
                'default_code': line.product_id.default_code,
                'package': line.package,
                'qty': line.qty,
                'net_weight': line.net_weight,
                'uom': line.uom_id.name,
                'src_location': line.src_location,
                'location_id': line.location_id.barcode or '',
                'state': line.state,
            }
        }
        return result

    @api.model
    def get_input_plate(self, task_id):
        #领取物品
        task = self.browse(task_id)
        task.write({'state': 'process'})
        line = task.line_ids[0]
        line.write({'state': 'process'})
        res = self.get_line_data(line)
        return res
        # return {
        #     'code': '201',
        #     'data': {
        #         'id': task.id,
        #         'product': line.product_id.name,
        #         'default_code': line.product_id.default_code,
        #         'package': line.package,
        #         'qty': line.qty,
        #         'net_weight': line.net_weight,
        #         'uom': line.uom_id.id,
        #         'src_location': line.src_location,
        #         'location_id': line.location_id.barcode,
        #         'state': line.state,
        #     },
        # }
    @api.model
    def get_input_task(self):
        # 登录后获取任务
        # process_task = self.search([('state', '=', 'assigned'), ('assign_to', '=', self.env.uid)])
        assign_task = self.search([('state', '=', 'assigned'), ('assign_to', '=', self.env.uid)])
        process_task = self.search([('state', '=', 'process'), ('assign_to', '=', self.env.uid)])
        todo_task = self.search([('state', '=', 'draft')], limit=1)
        #检查是否有一分配，但是为领取的单据
        if assign_task:
            return {
                'code': '200',
                'data': {
                    'id': assign_task.id,
                    'plate': assign_task.plate_id.name,
                    'user_id': assign_task.user_id.name,
                }
            }
        #检查是否有未完成的单（处理中，拆分），拆分的单据默认最后处理
        if process_task:
            # line = self.env['batar.input.line'].search([('input_id', '=', process_task.id), ('state', '=', 'process')], limit=1, order='sequence desc')
            line = self.env['batar.input.line'].search([('input_id', '=', process_task.id), ('state', '=', 'process')],limit=1)
            draft_line = self.env['batar.input.line'].search([('input_id', '=', process_task.id), ('state', '=', 'draft')],limit=1)
            split_line = self.env['batar.input.line'].search([('input_id', '=', process_task.id),
                                                              ('state', 'in', ['split', 'weight'])], order='split_sequence')
            # split_line = self.env['batar.input.line'].search(
            #     [('input_id', '=', process_task.id), ('state', '=', 'split')], order='split_sequence')
            if line:
                result = self.get_line_data(line)
                return result
            #等待称重
            if split_line:
                #返回需称重明细
                split_value = []
                for i in  split_line:
                    vals = {
                        'id': i.id,
                        'product': i.product_id.name,
                        'default_code': i.product_id.default_code,
                        'package': i.package,
                        'src_location': i.src_location,
                        'qty': i.qty,
                        'sequence': i.sequence,
                        'net_weight': i.net_weight,
                        'uom': i.uom_id.name,
                    }
                    split_value.append(vals)
                return {
                    'code': '203',
                    'data': split_value,
                }
            if draft_line:
                draft_line.write({'state': 'process'})
                result = self.get_line_data(draft_line)
                return result
            #全部上架完成，等待确认。
            if all([a.state == 'putaway' for a in process_task.line_ids]):
                last_line = process_task.line_ids.sorted(key=lambda x: x.sequence, reverse=True)[0]
                return {
                    'code': '400',
                    'data': {
                        'input_id': process_task.id,
                        # 'line_id': last_line.id,
                        'id': last_line.id,
                        'product': last_line.product_id.name,
                        'default_code': last_line.product_id.default_code,
                        'package': last_line.package,
                        'qty': last_line.qty,
                        'net_weight': last_line.net_weight,
                        'uom': last_line.uom_id.name,
                        'src_location': last_line.src_location,
                        'location_id': last_line.location_id.barcode or '',
                        'state': last_line.state,
                    },
                }
        # 分派未分配的任务
        elif todo_task:
            todo_task.write({
                'assign_to': self.env.uid,
                'state': 'assigned',
            })
            # line = todo_task.line_ids[0]
            # line.write({'state': 'process'})
            result = {
                'code': '200',
                'data': {
                    'id': todo_task.id,
                    # 'product': line.product_id.name,
                    # 'default_code': line.product_id.default_code,
                    # 'package': line.package,
                    # 'qty': line.qty,
                    # 'net_weight': line.net_weight,
                    # 'uom': line.uom_id.id,
                    # 'src_location': line.src_location,
                    # 'location_id': line.location_id.barcode,
                    # 'state': line.state,
                    'plate': todo_task.plate_id.name,
                    'user_id': todo_task.user_id.name,
                }
            }
            return result
        else:
            result = {
                'code': '500',
                'data': {}
            }
            return result
    @api.model
    def get_pre_line(self, line_id):
        #上一条任务
        line = self.env['batar.input.line'].browse([line_id])
        if line.sequence == 1:
            result = {
                'code': '500',
                'data': {},
            }
            return result
        else:
            pre_sequence = line.sequence - 1
            pre_line = self.env['batar.input.line'].search([('sequence', '=', pre_sequence), ('input_id', '=', line.input_id.id)])
            result = self.get_line_data(pre_line)
            return result
    @api.model
    def get_next_line(self, line_id, qty, location):
        # 下一条任务
        line = self.env['batar.input.line'].browse([line_id])
        des_location = self.env['stock.location'].search([('barcode', '=', location)])
        # split_task = self.env['batar.input.line'].search([('state', '=', 'split')])
        # split_task = self.env['batar.input.line'].search([('state', 'in', ['split', 'draft'])])
        split_task = self.env['batar.input.line'].search([('state', 'in', ['split', 'draft', 'weight'])])
        reserve_location = [a.location_id for a in split_task]
        maxsequence = max([a.sequence for a in line.input_id.line_ids])
        max_split_sequence = max([a.split_sequence for a in line.input_id.line_ids])

        # next_line = self.env['batar.input.line'].search(
        #     [('input_id', '=', line.input_id.id), ('sequence', '=', line.sequence + 1), ('state', 'not in', ['split', 'putaway'])])
        next_line = self.env['batar.input.line'].search([('input_id', '=', line.input_id.id), ('state', '=', 'draft')], limit=1)
        # 输入的库位不存在
        if not des_location:
            result = {
                'code': '501',
                'data': {},
            }
            return result
        #库位被预定
        if des_location in reserve_location:
            return {
                'code': '502',
                'data': {},
            }
            # 拆分，直到当前产品全部预定库位
        if qty < line.qty:
            # if next_line:
            #     next_line.write({'state': 'process'})
            split_line = line.copy({'net_weight': 0, 'gross_weight': 0, 'qty': line.qty - qty, 'location_id': None,'state': 'process'})
            line.write({'net_weight': 0, 'gross_weight': 0, 'qty': qty, 'state': 'split', 'location_id': des_location.id})
            for i in line.input_id.line_ids:
                if i.sequence > line.sequence:
                    i.sequence +=1
            if line.split_sequence:
                line.write({'src_location': 'C' + str(line.split_sequence)})
                split_line.write({'split_sequence': max_split_sequence + 1})
            else:
                line.write({'split_sequence': max_split_sequence + 1, 'src_location': 'C' + str(max_split_sequence + 1)})
                split_line.write({'split_sequence': max_split_sequence + 2})
            if max_split_sequence == 0:
                line.write({'split_sequence': 1, 'src_location': 'C1'})
                split_line.write({'split_sequence': 2})
            split_line.write({'sequence': line.sequence + 1})
            result = self.get_line_data(split_line)
            return result
        line.write({'location_id': des_location.id})
        # 增加库存移动
        # self.move_create(line)
        if line.net_weight == 0:
            line.write({'state': 'split', 'src_location': 'C' + str(line.split_sequence)})
            todo = self.env['batar.input.line'].search([('input_id', '=', line.input_id.id), ('state', '=', 'process')], limit=1)
            if todo:
                result = self.get_line_data(todo)
                return result
        else:
            line.write({'state': 'putaway'})
            self.move_create(line)
        if next_line:
            next_line.write({'state': 'process'})
            result = self.get_line_data(next_line)
            return result
        else:
            # wait_weight = self.env['batar.input.line'].search([('state', '=', 'split'), ('input_id', '=', line.input_id.id)], order='split_sequence')
            wait_weight = self.env['batar.input.line'].search(
                [('state', 'in', ['split', 'weight']), ('input_id', '=', line.input_id.id)], order='split_sequence')
            if not wait_weight:
                #全部上架完成
                return {
                    'code': '400',
                    'data': {
                        'input_id': line.input_id.id,
                        'id': line.id,
                        'product': line.product_id.name,
                        'default_code': line.product_id.default_code,
                        'package': line.package,
                        'qty': line.qty,
                        'net_weight': line.net_weight,
                        'uom': line.uom_id.name,
                        'src_location': line.src_location,
                        'location_id': line.location_id.barcode or '',
                        'state': line.state,
                        # 'line_id': line.id
                    },
                }
            else:
                #返回需称重明细
                result = []
                for i in  wait_weight:
                    vals = {
                        'id': i.id,
                        'product': i.product_id.name,
                        'default_code': i.product_id.default_code,
                        'package': i.package,
                        'src_location': i.src_location,
                        'qty': i.qty,
                        'sequence': i.sequence,
                        'net_weight': i.net_weight,
                        'uom': i.uom_id.name,
                    }
                    result.append(vals)
                return {
                    'code': '203',
                    'data': result,
                }
    # @api.model
    # def todo_weight(self, line_id, location=None):
    #     #称重明细的下一条处理
    #     line = self.env['batar.input.line'].browse(line_id)
    #     input_order = line.input_id
    #     if any([a.net_weight == 0 for a in input_order.line_ids]):
    #         #称重未完成
    #         return {
    #             'code': '503',
    #             'data': {},
    #         }
    #     else:
    #         next_line = self.env['batar.input.line'].search([('state', '=', 'split'), ('input_id', '=', input_order.id)], limit=1)
    #         if next_line:
    #             next_line.write({'state': 'process'})
    #             if location:
    #                 des_location = self.env['stock.location'].search([('barcode', '=', location)])
    #                 line.write({'location_id': des_location.id, 'state': 'putaway'})
    #             result = {
    #                 'code': '201',
    #                 'data': {
    #                     'id': next_line.id,
    #                     'product': next_line.product_id.name,
    #                     'default_code': next_line.product_id.default_code,
    #                     'package': next_line.package,
    #                     'net_weight': next_line.net_weight,
    #                     'uom': next_line.uom_id.id,
    #                     'src_location': next_line.src_location,
    #                     'state': next_line.state,
    #                     'qty': next_line.qty,
    #                 }
    #             }
    #             return result
    #         else:
    #             return {
    #                 'code': '400',
    #                 'data': {},
    #             }
    @api.model
    def confirm_putaway(self, input_id):
        # input_order = self.browse(input_id)
        input_order = self.search([('id', '=', input_id)])
        if all([a.state == 'putaway' for a in input_order.line_ids]) and input_order:
            input_order.move_ids.action_done()
            input_order.line_ids.write({'state': 'done'})
            input_order.write({'state': 'done'})
            input_order.plate_id.write({'state': 'pick_done'})
            return True
        else:
            return False

class InputLine(models.Model):
    _name = 'batar.input.line'
    _order = 'sequence'

    input_id = fields.Many2one('batar.input.mobile', string='Input Task', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    sequence = fields.Integer(string='Sequence')
    split_sequence =fields.Integer(string='Split Sequence')
    src_location = fields.Char(string='Pan Wei', required=True)
    location_id = fields.Many2one('stock.location', string='Location')
    net_weight = fields.Float(string='Net Weight', digits=dp.get_precision('Batar Price'))
    gross_weight = fields.Float(string='Gross Weight', digits=dp.get_precision('Batar Price'))
    uom_id = fields.Many2one(related='product_id.uom_id', string="Uom")
    package = fields.Char(string='Package Ref')
    qty = fields.Float(string='qty', digits=dp.get_precision('Batar Price'))
    state = fields.Selection([('draft', 'Draft'), ('process', 'Process'), ('split', 'Split'),('weight',"weight"), ('putaway', 'Putaway'), ('done', 'Done'), ('cancel', 'Cancel')], string='State', default='draft')


