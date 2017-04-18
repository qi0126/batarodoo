# -*- coding: utf-8 -*-
from openerp import api, fields, models

class Zhanting(models.Model):
    _inherit = 'zhanting'

    def mobile_pick_process(self, qty, op):
        mobile_obj = self.env['mobile.picking.line']
        mobile_task = mobile_obj.search([('operation_id', '=', op)], limit=1).pick_id
        if mobile_task.state == 'draft':
            res = super(Zhanting, self).mobile_pick_process(qty, op)
            return res
        #分拣台上称重时的退货
        if mobile_task.state == 'process':
            mobile_line = mobile_obj.search([('operation_id', '=', op), ('is_return', '=', False)])
            if mobile_line:
                #退货包
                package_vals = {
                    'product_id': mobile_line.product_id.id,
                    'product_code': mobile_line.product_id.default_code,
                    'partner_id': mobile_task.partner_id.id,
                    'qty': qty,
                    'mobile_picking': mobile_task.id,
                    'is_return': True,
                }
                #分拣退货明细
                package_return = self.env['batar.package'].create(package_vals)
                vals = {
                    'product_id': mobile_line.product_id.id,
                    'qty': qty,
                    'src_location': mobile_line.src_location.id,
                    'state': 'draft',
                    'operation_id': mobile_line.operation_id.id,
                    'is_return': True,
                    'des_location': package_return.name,
                }
                mobile_task.write({'line_ids': [(0, 0, vals)]})
            # mobile_line = mobile_obj.search([('operation_id', '=', op), ('is_return', '=', False), ('qty', '=', qty)], limit=1)
            # if mobile_line:
            #     vals = {
            #         'product_id': mobile_line.product_id.id,
            #         'qty': qty,
            #         'src_location': mobile_line.src_location.id,
            #         'state': 'draft',
            #         'operation_id': mobile_line.operation_id.id,
            #         'is_return': True,
            #     }
            #     mobile_task.write({'line_ids': [(0,0,vals)]})
            # else:
            #     mobile_lines = mobile_obj.search([('operation_id', '=', op), ('is_return', '=', False)], order='qty desc')
            #
            #     for line in mobile_lines:
            #         if qty == 0:
            #             break
            #         elif qty >= line.qty:
            #             vals['qty'] = line.qty
            #             qty -= line.qty
            #         else:
            #             vals['qty'] = qty
            #             qty = 0
            #         vals = {
            #             'product_id': line.product_id.id,
            #             'src_location': line.src_location.id,
            #             'state': 'draft',
            #             'operation_id': line.operation_id.id,
            #             'is_return': True,
            #         }
            #         mobile_task.write({'line_ids': [(0, 0, vals)]})




