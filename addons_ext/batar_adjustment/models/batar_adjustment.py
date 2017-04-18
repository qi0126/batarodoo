# -*- coding: utf-8 -*-
from openerp import fields, models, api
from datetime import datetime
from openerp.exceptions import UserError
import pytz

localtz = pytz.timezone('Asia/Shanghai')

class BatarAdjustment(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    def prepare_location(self):
        self.ensure_one()
        return True
class Stockmove(models.Model):
    _inherit = 'stock.move'

    adjustment_ids = fields.Many2one('batar.location.adjustment', string="Location Adjustment")

class LocationAdjustment(models.Model):
    _name = 'batar.location.adjustment'

    name = fields.Char(default=lambda self:datetime.now(localtz).strftime('%Y-%m-%d %H:%M:%S'), readonly=True)
    location_id = fields.Many2one('stock.location', string="Location", required=True, readonly=True, states={'draft': [('readonly', False)]})
    move_ids = fields.One2many('stock.move', 'adjustment_ids', string="Move lines", readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('process', 'Process'), ('done', 'Done')], default='draft')
    date = fields.Datetime('Location Adjustment Date', required=True, readonly=True, default=lambda self:datetime.now(localtz).strftime('%Y-%m-%d %H:%M:%S'))

    def compute_inuse(self, location):
        total = 0.0
        quant_obj = self.env['stock.quant']
        res = {}
        res ['location'] = location
        res['products'] = {}
        for line in quant_obj.search([('location_id', '=', location)]):
            if line.product_id.id in res['products'].keys():
                total += line.product_id.product_volume * line.qty
                res['products'][line.product_id.id] = total
            else:
                total = line.product_id.product_volume * line.qty
                res['products'][line.product_id.id] = total
            # total += line.product_id.product_volume * line.qty

        return res

    @api.multi
    def location_adjustment(self):
        self.ensure_one()
        location = self.location_id
        location_obj = self.env['stock.location']
        product_obj = self.env['product.product']
        move_lines = []
        domain = [('location_id', '=', location.id), ('is_sample', '=', False), ('child_ids', '!=', None)]
        locations = location_obj.search(domain)
        res = []
        #托盘总数
        location_src = []
        location_des = []
        has_done = False
        if not locations:
            raise UserError(u'没有需要调整的库位')
        else:
            for i in locations:
                val = []
                inuse = 0
                for c in i.child_ids:
                    # qty = self.compute_inuse(c.id)
                    qty = sum([x for x in self.compute_inuse(c.id)['products'].values()])
                    if qty > 0:
                        inuse += qty
                    else:
                        continue
                if inuse > 0:
                    val.append(i.id)
                    val.append(inuse)
                    avaliable = i.location_volume - inuse
                    val.append(avaliable)
                else:
                    continue
                res.append(val)
            # 按照托盘中的已用容量按高到低排序
            res.sort(key=lambda x:x[1])
            # 取得总库存数，并计算可空余盘
            location_sum = int((sum([x[1] for x in res]) + 60 - 1 )/60)
            # total = divmod(sum([x[1] for x in res]), 60)
            # if total[1] > 0:
            #     location_sum = total[0] + 1
            if location_sum == len(res):
                raise UserError(u'无法空余出新的托盘')
            else:
                for i in range(0, (len(res) - location_sum)):
                    parent_location = res[i][0]
                    for c in location_obj.browse(parent_location).child_ids:
                        # qty = self.compute_inuse(c.id)
                        #计算当前子库位的已用容量值
                        qty = sum([x for x in self.compute_inuse(c.id)['products'].values()])
                        if qty > 0:
                            vals = self.compute_inuse(c.id)
                            location_src.append(vals)
                        else:
                            continue
                res.sort(key=lambda x: x[1], reverse=True)
                for j in res:
                    for c in location_obj.browse(j[0]).child_ids:
                        qty = sum([x for x in self.compute_inuse(c.id)['products'].values()])
                        if qty == 0:
                            location_des.append(c.id)
                        else:
                            continue
                        #目前按照一个产品一个子库位来映射移库,如果两边库位相等则退出所有循环
                        if len(location_des) == len(location_src):
                            has_done = True
                            break
                    if has_done:
                        break
                for x in range(len(location_src)):
                    for y in location_src[x]['products'].keys():
                        vals = {
                            'product_id': y,
                            'location_id': location_src[x]['location'],
                            'location_dest_id': location_des[x],
                            'product_uom': product_obj.browse(y).uom_id.id,
                            'product_uom_qty': location_src[x]['products'][y],
                            'name': 'INV:adj',
                            'origin': 'AD:' + self.name
                        }
                        move_lines.append((0, 0, vals))
                return self.write({'move_ids': move_lines, 'state': 'process'})

    @api.multi
    def action_done(self):
        for line in self:
            move_obj = line.move_ids
            move_obj.action_done()
            self.write({'state': 'done'})




