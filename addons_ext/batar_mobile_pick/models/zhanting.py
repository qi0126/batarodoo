# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.exceptions import UserError

class Zhanting(models.Model):
    _inherit = 'zhanting'

    @api.model
    def confirm_change_pick_return(self, order_line=None, abs_change_qty=0, type='back'):
        res = super(Zhanting, self).confirm_change_pick_return()
        pick_ids = order_line.pick_ids
        mobile_obj = self.env['mobile.pick.line']
        search_list = [('picking_id', 'in', [line.id for line in pick_ids]),('product_id','=',order_line.product_id.id), ('picking_id.state', '!=', 'done')]
        stock_operations = self.env['stock.pack.operation'].search(search_list)
        if type=='back':
            for stock_operation in stock_operations:
                can_return_qty = int(stock_operation.product_qty - stock_operation.qty_return)
                #退货数大于可退数时，取可退数
                if abs_change_qty > can_return_qty:
                    abs_change_qty -= can_return_qty
                mobile_lines = mobile_obj.search([('operation_id', '=', stock_operation.id), ('state', '!=', 'done')])
                mobile_done = mobile_obj.search([('operation_id', '=', stock_operation.id), ('state', '=', 'done')])
                #检查所有的有退货的且是未完成的操作单据
                if mobile_lines:
                    for line in mobile_lines:
                        if abs_change_qty >= line.qty:
                            line.unlink()
                            abs_change_qty -= line.qty
                        else:
                            line.write({'qty': line.qty - abs_change_qty})
                            abs_change_qty = 0
                            break
                elif mobile_done and abs_change_qty >0:
                    for order in mobile_done:
                        if abs_change_qty >= order.qty:
                            vals = {
                                'product_id': order.product_id.id,
                                'qty': order.qty,
                                'src_location': order.src_location,
                                'des_location': order.des_location,
                                'state': 'draft',
                                'operation_id': order.operaton_id.id,
                                'is_return': True,
                            }
                            self.env['batar.mobile.pick'].browse([order.pick_id.id]).write({'line_ids': [(0,0,vals)]})
                            abs_change_qty -= line.qty
                        else:
                            vals = {
                                'product_id': order.product_id.id,
                                'qty': line.qty - abs_change_qty,
                                'src_location': order.src_location,
                                'des_location': order.des_location,
                                'state': 'draft',
                                'operation_id': order.operaton_id.id,
                                'is_return': True,
                            }
                            self.env['batar.mobile.pick'].browse([order.pick_id.id]).write({'line_ids': [(0, 0, vals)]})
                            abs_change_qty = 0
                            break
                else:
                    raise UserError('分拣单数据与手机分拣数据不符！')
        return res
