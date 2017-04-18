# -*- coding: utf-8 -*-
from openerp import api, fields, models

class MobilePick(models.Model):
    _inherit = 'batar.mobile.picking'

    zhanting_id = fields.Many2one('batar.customer.sale', string='Zhanting')

    @api.model
    def get_priority_task(self, pick):
        #分拣单中加入展厅单的引用
        res = super(MobilePick, self).get_priority_task(pick)
        pick = self.env['mobile.picking.line'].browse(res['data']['id']).pick_id
        zhanting_obj = self.env['batar.customer.sale']
        zhanting_order = zhanting_obj.search([('partner_id', '=', pick.partner_id.id), ('state', '=', 'process')])
        pick.write({'zhanting_id': zhanting_order.id})
        return res
class Zhanting(models.Model):
    _inherit = 'zhanting'

    def process_weight_return(self, p):
        for p_package in p.package_ids:
            src_locations = p.line_ids.filtered(lambda r: r.product_id == p_package.product_id).mapped('src_location')
            for location in src_locations:
                qty_return = sum(p.line_ids.filtered(lambda
                                                         r: r.product_id == p_package.product_id and r.src_location == location and r.is_return == True).mapped(
                    'qty'))
                qty_pick = sum(p.line_ids.filtered(lambda
                                                       r: r.product_id == p_package.product_id and r.src_location == location and r.is_return == False).mapped(
                    'qty'))
                qty_avaliable = qty_pick - qty_return
                if qty_avaliable >= p_package.qty:
                    vals = {
                        'sequence': 0,
                        'is_return': True,
                        'state': 'draft',
                        'qty': p_package.qty,
                        'des_location': p_package.name,
                        'src_location': location.id,
                        'product_id': p_package.product_id.id,
                    }
                    p.write({'line_ids': [(0, 0, vals)]})
                    break
                else:
                    vals = {
                        'sequence': 0,
                        'is_return': True,
                        'state': 'draft',
                        'qty': qty_avaliable,
                        'des_location': p_package.name,
                        'src_location': location.id,
                        'product_id': p_package.product_id.id,
                    }
                    p.write({'line_ids': [(0, 0, vals)]})
                    p_package.qty -= qty_avaliable

    @api.model
    def cancel_all_order(self, offset=0, limit=20, location_id=None):
        res = super(Zhanting, self).cancel_all_order(offset=0, limit=20, location_id=location_id)
        if res:
            user = self.env['res.users'].search([('id', '=', self._context['uid'])])
            customer_id = user.current_customer and user.current_customer.id
            if not customer_id:
                return False
            zhanting_obj = self.env['batar.customer.sale']
            zhanting_order = zhanting_obj.search([('partner_id', '=', customer_id), ('state', '=', 'process')])
            mobile_obj = self.env['batar.mobile.picking']
            mobile_orders = mobile_obj.search([('zhanting_id', '=', zhanting_order.id)])
            internal_obj = self.env['batar.sample.trans']
            draft = mobile_orders.filtered(lambda x: x.state == 'draft')
            process = mobile_orders.filtered(lambda x: x.state == 'process')
            done = mobile_orders.filtered(lambda x: x.state == 'done')
            wh = self.env['stock.warehouse'].search([], limit=1)
            pz = wh.wh_pack_stock_loc_id
            op = wh.wh_output_stock_loc_id
            """
            把对应分拣单分为三组：草稿，处理中，完成。
            草稿单：明细为草稿的，直接删除；
                    明细为处理和完成的，生成退货任务
            处理中：称重未完成的，根据盘位退货
                   称重已完成的，根据包号退货
            完成： pick单据同一个需求组的PACK,OUT单据状态，
                   pack--assigned ，则pack退货调拨
                   out--assigned， 则out退货调拨
            """
            if draft:
                draft_lines = draft.mapped('line_ids').filtered(lambda r:r.state == 'draft' and r.is_return == False)
                if draft_lines:
                    draft_lines.unlink()
                for mobile_line in draft.line_ids:
                    #已存在的退货数量
                    mobile_return = draft.mapped('line_ids').filtered(lambda r:r.is_return == True and r.product_id == mobile_line.product_id and r.des_location == mobile_line.des_location)
                    return_qty = 0
                    if mobile_return:
                        return_qty = sum(mobile_return.mapped('qty'))
                    qty = mobile_line.qty - return_qty
                    mobile_line.copy({'sequence': 0, 'is_return': True, 'state': 'draft', 'qty': qty})

            if process:
                for p in process:
                    #全部未称重，按托盘位置退货
                    if all([a.state == 'draft' for a in p.package_ids]):
                        for p_line in p.line_ids:
                            p_return = p.mapped('line_ids').filtered(lambda r: r.is_return == True and r.product_id == p_line.product_id and r.src_location == p_line.src_location)
                            return_qty = 0
                            if p_return:
                                return_qty = sum(p_return.mapped('qty'))
                            qty = p_line.qty - return_qty
                            p_line.copy({'sequence': 0, 'is_return': True, 'state': 'draft', 'qty': qty})
                    #全部已称重，按包号退货
                    elif all([a.state == 'done' for a in p.package_ids]):
                        self.process_weight_return(p)
                    else:
                        #部分称重，则全部修改状态为完成，按照完成退货
                        undone_package = p.package_ids.filtered(lambda r:r.state != 'done')
                        undone_package.write({'state': 'done'})
                        self.process_weight_return(p)

            if done:
                # groups = done.pick_ids.mapped('group_id')
                pack_type_id = self.env['stock.picking.type'].with_context(lang='en').search([('name', 'ilike', 'Pack')], limit=1).id
                out_type_id = self.env['stock.picking.type'].with_context(lang='en').search([('name', 'ilike', 'Delivery Orders')], limit=1).id
                pack_lines = []
                out_lines = []
                pack_return = None
                out_return =None
                #把待验货的所有退货合并一张单据，把所有已验货的所有退货合并一张单据
                for done_line in done:
                    groups = done_line.pick_ids.mapped('group_id')
                    pack_orders = self.env['stock.picking'].search([('group_id', 'in', groups.ids), ('picking_type_id', '=', pack_type_id)])
                    if all([a.state == 'assigned' for a in pack_orders]):
                        if not pack_return:
                            pack_return = internal_obj.create({'type': 'out', 'user_id': self.env.uid,
                                                               'ref': done_line.zhanting_id.name, 'location_id': pz.id, 'state': 'process'})
                        for package in done_line.package_ids:
                            vals = {
                                'product_id': package.product_id.id,
                                'ref': package.name,
                                'qty': package.qty,
                                'src_location': pz.id,
                            }
                            pack_lines.append((0,0,vals))
                    out_orders = self.env['stock.picking'].search([('group_id', 'in', groups.ids), ('picking_type_id', '=', out_type_id)])
                    if all([a.state == 'assigned' for a in out_orders]):
                        if not out_return:
                            out_return = internal_obj.create({'type': 'out', 'user_id': self.env.uid,
                                                              'ref': done_line.zhanting_id.name, 'location_id': op.id, 'state': 'process'})
                        for package in done_line.package_ids:
                            vals = {
                                'product_id': package.product_id.id,
                                'ref': package.name,
                                'qty': package.qty,
                                'src_location': op.id,
                            }
                            out_lines.append((0,0,vals))
                if pack_return:
                    pack_return.write({'line_ids': pack_lines})
                if out_return:
                    out_return.write({'line_ids': out_lines})
        # res = super(Zhanting, self).cancel_all_order(offset=0, limit=20, location_id=location_id)
        return res