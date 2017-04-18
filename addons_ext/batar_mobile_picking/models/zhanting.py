# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.exceptions import UserError

class Zhanting(models.Model):
    _inherit = 'zhanting'

    def mobile_pick_process(self, qty, op):
        mobile_obj = self.env['mobile.picking.line']
        mobile_lines = mobile_obj.search(
            [('operation_id', '=', op), ('state', '=', 'draft'), ('is_return', '=', False)])
        mobile_done = mobile_obj.search(
            [('operation_id', '=', op), ('state', 'in', ['done', 'process']), ('is_return', '=', False)])
        mobile_return = mobile_obj.search(
            [('operation_id', '=', op), ('state', '=', 'draft'), ('is_return', '=', True)], limit=1)
        # 检查所有的有退货的且是未完成的操作单据
        if mobile_lines:
            for mobile_line in mobile_lines:
                if qty >= mobile_line.qty:
                    qty -= mobile_line.qty
                    mobile_line.unlink()
                else:
                    mobile_line.write({'qty': mobile_line.qty - qty})
                    qty = 0
                    break
        elif mobile_return and qty > 0:
            total_qty = mobile_return.qty + qty
            mobile_return.write({'qty': total_qty})
            qty = 0
        elif mobile_done and qty > 0:
            for order in mobile_done:
                if qty >= order.qty:
                    vals = {
                        'product_id': order.product_id.id,
                        'qty': order.qty,
                        'src_location': order.src_location.id,
                        'des_location': order.des_location,
                        'state': 'draft',
                        'operation_id': order.operation_id.id,
                        'is_return': True,
                    }
                    self.env['batar.mobile.picking'].browse([order.pick_id.id]).write({'line_ids': [(0, 0, vals)]})
                    qty -= order.qty
                else:
                    vals = {
                        'product_id': order.product_id.id,
                        # 'qty': order.qty - abs_change_qty,
                        'qty': qty,
                        'src_location': order.src_location.id,
                        'des_location': order.des_location,
                        'state': 'draft',
                        'operation_id': order.operation_id.id,
                        'is_return': True,
                    }
                    self.env['batar.mobile.picking'].browse([order.pick_id.id]).write({'line_ids': [(0, 0, vals)]})
                    qty = 0
                    break

    @api.model
    def confirm_change_pick_return(self, order_line=None, abs_change_qty=0, type='back'):
        # def mobile_pick_process(qty, op):
        #     mobile_obj = self.env['mobile.picking.line']
        #     mobile_lines = mobile_obj.search(
        #         [('operation_id', '=', op), ('state', '=', 'draft'), ('is_return', '=', False)])
        #     mobile_done = mobile_obj.search([('operation_id', '=', op), ('state', 'in', ['done', 'process']), ('is_return', '=', False)])
        #     mobile_return = mobile_obj.search([('operation_id', '=', op), ('state', '=', 'draft'), ('is_return', '=', True)], limit=1)
        #     #检查所有的有退货的且是未完成的操作单据
        #     if mobile_lines:
        #         for mobile_line in mobile_lines:
        #             if qty >= mobile_line.qty:
        #                 qty -= mobile_line.qty
        #                 mobile_line.unlink()
        #             else:
        #                 mobile_line.write({'qty': mobile_line.qty - qty})
        #                 qty = 0
        #                 break
        #     elif mobile_return and qty > 0:
        #         total_qty = mobile_return.qty + qty
        #         mobile_return.write({'qty': total_qty})
        #         qty = 0
        #     elif mobile_done and qty >0:
        #         for order in mobile_done:
        #             if qty >= order.qty:
        #                 vals = {
        #                     'product_id': order.product_id.id,
        #                     'qty': order.qty,
        #                     'src_location': order.src_location.id,
        #                     'des_location': order.des_location,
        #                     'state': 'draft',
        #                     'operation_id': order.operation_id.id,
        #                     'is_return': True,
        #                 }
        #                 self.env['batar.mobile.picking'].browse([order.pick_id.id]).write({'line_ids': [(0,0,vals)]})
        #                 qty -= order.qty
        #             else:
        #                 vals = {
        #                     'product_id': order.product_id.id,
        #                     # 'qty': order.qty - abs_change_qty,
        #                     'qty': qty,
        #                     'src_location': order.src_location.id,
        #                     'des_location': order.des_location,
        #                     'state': 'draft',
        #                     'operation_id': order.operation_id.id,
        #                     'is_return': True,
        #                 }
        #                 self.env['batar.mobile.picking'].browse([order.pick_id.id]).write({'line_ids': [(0, 0, vals)]})
        #                 qty = 0
        #                 break

        if not order_line and abs_change_qty:
            return False, abs_change_qty
        pick_ids = order_line.pick_ids
        search_list = [('picking_id', 'in', [line.id for line in pick_ids]),
                       ('product_id', '=', order_line.product_id.id), ('picking_id.state', '!=', 'done')]
        stock_operations = self.env['stock.pack.operation'].search(search_list, order='qty_done asc, id desc')
        if type == 'exchange':
            for stock_operation in stock_operations:
                if stock_operation.product_qty >= abs_change_qty:
                    abs_change_qty = 0
                    break
                else:
                    abs_change_qty -= stock_operation.product_qty
        elif type == 'back':
            for stock_operation in stock_operations:
                can_return_qty = int(stock_operation.product_qty - stock_operation.qty_return)
                if abs_change_qty > can_return_qty:
                    stock_operation.qty_return += can_return_qty
                    self.mobile_pick_process(can_return_qty, stock_operation.id)
                    abs_change_qty -= can_return_qty
                else:
                    stock_operation.qty_return += abs_change_qty
                    self.mobile_pick_process(abs_change_qty, stock_operation.id)
                    abs_change_qty = 0
                    break
        if int(abs_change_qty) != 0:
            return False, abs_change_qty
        order_line.change_qty = 0
        order_line.exchange_qty = 0
        return True, abs_change_qty


        # change_qty_old = abs_change_qty
        # # res = super(Zhanting, self).confirm_change_pick_return(order_line, abs_change_qty, type)
        # pick_ids = order_line.pick_ids
        # mobile_obj = self.env['mobile.picking.line']
        # search_list = [('picking_id', 'in', [line.id for line in pick_ids]),('product_id','=',order_line.product_id.id), ('picking_id.state', 'not in', ['done', 'cancel'])]
        # stock_operations = self.env['stock.pack.operation'].search(search_list)
        # if type=='back':
        #     for stock_operation in stock_operations:
        #         can_return_qty = int(stock_operation.product_qty - stock_operation.qty_return)
        #         #退货数大于可退数时，取可退数
        #         if abs_change_qty > can_return_qty:
        #             # abs_change_qty -= can_return_qty
        #             abs_change_qty = can_return_qty
        #         # mobile_lines = mobile_obj.search([('operation_id', '=', stock_operation.id), ('state', '!=', 'done')])
        #         # mobile_done = mobile_obj.search([('operation_id', '=', stock_operation.id), ('state', '=', 'done')])
        #         mobile_lines = mobile_obj.search([('operation_id', '=', stock_operation.id), ('state', '=', 'draft'), ('is_return', '=', False)])
        #         mobile_done = mobile_obj.search([('operation_id', '=', stock_operation.id), ('state', 'in', ['done', 'process']), ('is_return', '=', False)])
        #         #检查所有的有退货的且是未完成的操作单据
        #         if mobile_lines:
        #             for mobile_line in mobile_lines:
        #                 if abs_change_qty >= mobile_line.qty:
        #                     abs_change_qty -= mobile_line.qty
        #                     mobile_line.unlink()
        #                 else:
        #                     mobile_line.write({'qty': mobile_line.qty - abs_change_qty})
        #                     abs_change_qty = 0
        #                     break
        #         elif mobile_done and abs_change_qty >0:
        #             for order in mobile_done:
        #                 if abs_change_qty >= order.qty:
        #                     vals = {
        #                         'product_id': order.product_id.id,
        #                         'qty': order.qty,
        #                         'src_location': order.src_location.id,
        #                         'des_location': order.des_location,
        #                         'state': 'draft',
        #                         'operation_id': order.operation_id.id,
        #                         'is_return': True,
        #                     }
        #                     self.env['batar.mobile.picking'].browse([order.pick_id.id]).write({'line_ids': [(0,0,vals)]})
        #                     abs_change_qty -= order.qty
        #                 else:
        #                     vals = {
        #                         'product_id': order.product_id.id,
        #                         # 'qty': order.qty - abs_change_qty,
        #                         'qty': abs_change_qty,
        #                         'src_location': order.src_location.id,
        #                         'des_location': order.des_location,
        #                         'state': 'draft',
        #                         'operation_id': order.operation_id.id,
        #                         'is_return': True,
        #                     }
        #                     self.env['batar.mobile.picking'].browse([order.pick_id.id]).write({'line_ids': [(0, 0, vals)]})
        #                     abs_change_qty = 0
        #                     break
        #         # else:
        #         #     raise UserError('分拣单数据与手机分拣数据不符！')
        # res = super(Zhanting, self).confirm_change_pick_return(order_line, change_qty_old, type)
        # return res