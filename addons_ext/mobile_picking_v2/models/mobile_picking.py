# -*- coding: utf-8 -*-
from openerp import api, fields, models, exceptions

class MobilePicking(models.Model):
    _inherit = 'batar.mobile.picking'

    package_ids = fields.One2many('batar.package', 'mobile_picking', string='Packages', readonly=True)



    @api.model
    def get_next_line(self, line_id, done_qty):
        """
        由之前的一张订单直接到出库完成改成新流程：
        1、在拣货中，如果当前客户有新的picking order则加入到任务中（在生成Pickingorder的同时）
        2、新加入打包称重阶段，此阶段如有退货，则全部称重完后再处理
        3、称重后无后续单，则交付
        """
        line = self.env['mobile.picking.line'].browse([line_id])
        task = line.pick_id
        if done_qty == line.qty:
            line.write({'state': 'done'})
            draft_order = self.env['mobile.picking.line'].search([('state', '=', 'draft'), ('pick_id', '=', task.id)])
            if not draft_order:
                #打包过程，默认每个产品规格一个包
                task.write({'state': 'process'})
                if line.is_return:
                    qty = line.operation_id.qty_done - line.qty
                else:
                    qty = line.operation_id.qty_done + done_qty
                line.operation_id.write({'qty_done': qty})
                products = list(set([a.product_id for a in task.line_ids]))
                package_lines = []
                for p in products:
                    qty_total = sum([a.qty for a in task.line_ids if a.is_return == False and a.product_id == p]) - sum([a.qty for a in task.line_ids if a.is_return == True and a.product_id == p])
                    ref = []
                    p_lines = self.env['mobile.picking.line'].search([('pick_id', '=', task.id), ('product_id', '=', p.id), ('is_return', '=', False)])
                    for x in p_lines:
                        if x.des_location not in ref:
                            ref.append(x.des_location)

                    if qty_total > 0:
                        vals = {
                            'qty': qty_total,
                            'product_id': p.id,
                            'ref': ','.join(ref),
                            'partner_id': task.partner_id.id,
                            'product_code': p.default_code,
                        }
                        package_lines.append((0,0,vals))
                task.write({'package_ids': package_lines})
                pick_total = sum(x.qty for x in task.line_ids if not x.is_return)
                return_total = sum(x.qty for x in task.line_ids if x.is_return)
                result = {
                    'code': '400',
                    'data': {
                        'total': pick_total - return_total
                    }
                }
                return result
        res = super(MobilePicking, self).get_next_line(line_id, done_qty)
        return res
    @api.model
    def wait_task(self, line_id):
        """
        完成分拣后，等待称重。
        1：称重完成后，无新的退货，直接交付
        2：称重完成后，有新的退货，则返回退货明细
        """
        line = self.env['mobile.picking.line'].browse([line_id])
        task = line.pick_id
        new_returns = self.env['mobile.picking.line'].search([('pick_id', '=', task.id), ('is_return', '=', True), ('state', '=', 'draft')])
        if all(a.state == 'done' for a in task.line_ids):
            if all(p.state == 'done' for p in task.package_ids):
                return {
                    'code': '400',
                    'data': {},
                }
        if new_returns:
            des_location = ''
            for return_line in new_returns:
                flag = False
                return_qty = return_line.qty
                packages = self.env['batar.package'].search([('mobile_picking', '=', task.id),
                                                             ('is_return', '=', False),
                                                             ('product_id', '=', return_line.product_id.id)])
                for p in packages:
                    if return_qty == 0:
                        flag = True
                        break
                    elif return_qty >= p.qty:
                        #如果退货明细行数量大于包数，则整包退货
                        p.write({'is_return', '=', True})
                        des_location += p.name + ','
                        return_qty -= p.qty
                        # else:
    @api.multi
    def package_print(self):
        self.ensure_one()
        if all([a.state == 'done' for a in self.package_ids]):
            if self.state == 'process':
                for x in self.pick_ids:
                    return_pick = sum(y.qty_return for y in x.pack_operation_product_ids)
                    if return_pick > 0:
                        backorder_wiz_id = x.do_new_transfer()['res_id']
                        backorder_wiz = self.env['stock.backorder.confirmation'].browse([backorder_wiz_id])
                        backorder_wiz.process_cancel_backorder()
                    else:
                        x.do_new_transfer()
                self.write({'state': 'done'})
            return self.package_ids.print_package_tag()
        else:
            raise exceptions.ValidationError(u'存在未称重的包！')

    @api.model
    def cancel_confirm(self, line_id):
        line = self.env['mobile.picking.line'].browse(line_id)
        if line:
            line.pick_id.write({'state': 'done'})
            return True
        else:
            return False

    @api.multi
    def test_confirm(self):
        self.ensure_one()
        return self.write({'state': 'done'})




class SplitPackage(models.Model):
    _inherit = 'batar.package'

    mobile_picking = fields.Many2one('batar.mobile.picking', string='Mobile Picking')
    ref = fields.Char(string='Ref Panwei')
    is_return = fields.Boolean(string='Is Return', default=False)

    @api.multi
    def print_package_tag(self):
        return self.env['report'].get_action(self, 'mobile_picking_v2.report_package')

class Splitwizard(models.TransientModel):
    _inherit = 'batar.split.package'

    @api.multi
    def confirm(self):
        self.ensure_one()
        package_obj = self.env['batar.package']
        package = package_obj.browse(self._context.get('active_ids'))[0]
        if package.mobile_picking:
            balance = package.qty - self.qty
            package.write({'qty': balance, 'net_weight': 0, 'weight': 0})
            vals = {
                'qty': self.qty,
                'product_id': package.product_id.id,
                'ref': package.ref,
                'partner_id': package.mobile_picking.partner_id.id,
                'product_code': package.product_id.default_code,
            }
            package.mobile_picking.write({'package_ids': [(0,0,vals)]})
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'batar.mobile.picking',
                'type': 'ir.actions.act_window',
                'res_id': package.mobile_picking.id,
            }
        res = super(Splitwizard, self).confirm()
        return res