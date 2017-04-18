# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.exceptions import UserError
from openerp.tools.translate import _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import pytz

localtz = pytz.timezone('Asia/Shanghai')

class Product(models.Model):
    _inherit = 'product.product'

    inv_adjustment = fields.Boolean(string='Inventory adjustment', default=False)

class Batar_inventory(models.Model):
    _inherit = 'stock.inventory'


    name = fields.Char(default=lambda self: datetime.now(localtz).strftime('%Y-%m-%d %H:%M:%S'), states={'draft': [('readonly', True)]})
    set_total = fields.Float(string='Total', states={'done': [('readonly', True)]})
    date_end = fields.Char(string='End date', readonly=True)


    @api.multi
    def reset_real_total(self):
        for inv in self:
            total = sum([x.second_uom for x in inv.line_ids])
            if inv.set_total:
                inv_adjustment = False
                for line in inv.line_ids:
                    if line.product_id.inv_adjustment:
                        second_uom = inv.set_total - total + line.second_uom
                        line.write({'second_uom': second_uom})
                        return True
                    else:
                        inv_adjustment = line.product_id.inv_adjustment
                        continue
                if not inv_adjustment:
                    raise UserError(u'请添加库存调整的调库产品')

    
    @api.multi
    def action_done(self):
        # date_end = datetime.now(localtz).strftime('%m/%d/%Y %H:%M:%S')
        # self.write({'date_end': date_end})
        for inv in self:
            for inventory_line in inv.line_ids:
                diff = inventory_line.product_qty - inventory_line.theoretical_qty
                diff_seconduom = inventory_line.second_uom - inventory_line.theoretical_secondqty
                if (diff > 0 and diff_seconduom < 0) or (diff < 0 and diff_seconduom > 0):
                    raise UserError(u'调整数据有误,关联产品为:"%s".' % inventory_line.product_id.name)
                else:
                    return super(Batar_inventory, self).action_done()

    def _get_inventory_lines(self, cr, uid, inventory, context=None):
        location_obj = self.pool.get('stock.location')
        product_obj = self.pool.get('product.product')
        location_ids = location_obj.search(cr, uid, [('id', 'child_of', [inventory.location_id.id])], context=context)
        domain = ' location_id in %s'
        args = (tuple(location_ids),)
        if inventory.partner_id:
            domain += ' and owner_id = %s'
            args += (inventory.partner_id.id,)
        if inventory.lot_id:
            domain += ' and lot_id = %s'
            args += (inventory.lot_id.id,)
        if inventory.product_id:
            domain += ' and product_id = %s'
            args += (inventory.product_id.id,)
        if inventory.package_id:
            domain += ' and package_id = %s'
            args += (inventory.package_id.id,)

        cr.execute('''
           SELECT product_id, sum(qty) as product_qty, sum(second_uom) as second_uom, location_id, lot_id as prod_lot_id, package_id, owner_id as partner_id
           FROM stock_quant WHERE''' + domain + '''
           GROUP BY product_id, location_id, lot_id, package_id, partner_id
        ''', args)
        vals = []
        for product_line in cr.dictfetchall():
            # replace the None the dictionary by False, because falsy values are tested later on
            for key, value in product_line.items():
                if not value:
                    product_line[key] = False
            product_line['inventory_id'] = inventory.id
            product_line['theoretical_qty'] = product_line['product_qty']
            product_line['theoretical_secondqty'] = product_line['second_uom']
            if product_line['product_id']:
                product = product_obj.browse(cr, uid, product_line['product_id'], context=context)
                product_line['product_uom_id'] = product.uom_id.id
            vals.append(product_line)
        return vals



class Batar_inventory_line(models.Model):
    _inherit = 'stock.inventory.line'

    theoretical_secondqty = fields.Float(string='Theoretical Secondqty', readonly=True, compute='_get_secondqty', store=True)
    second_uom = fields.Float(string='Second uom')
    # inv_adjustment = fields.Boolean(string='Inventory adjustment')
    #
    # @api.onchange('product_id')
    # def onchangge_inv_adjustment(self):
    #     if self.product_id:
    #         self.inv_adjustment = self.product_id.inv_adjustment
    # @api.onchange('product_id', 'location_id')
    # def onchange_seconduom(self):
    #     print 'enter onchange '
    #     quant_obj = self.env['stock.quant']
    #     vals = {}
    #     if self.product_id and self.location_id:
    #         quants = quant_obj.search([('product_id', '=', self.product_id.id), ('location_id', '=', self.location_id.id)])
    #         tot_qty = sum([x.second_uom for x in quants])
    #         vals['second_uom'] = tot_qty
    #         vals['theoretical_secondqty'] = tot_qty
    #     self.update(vals)
    #     return {}
    @api.multi
    def onchange_createline(self, location_id=False, product_id=False, uom_id=False, package_id=False, prod_lot_id=False, partner_id=False, company_id=False):
        res = {'value': {}}
        quant_obj = self.env['stock.quant']
        if product_id and location_id:
            dom = [('location_id', '=', location_id), ('product_id', '=', product_id)]
            quants = quant_obj.search(dom)
            tot_qty = sum([x.second_uom for x in quants])
            th_qty = sum ([x.qty for x in quants])
            res['value']['theoretical_qty'] = th_qty
            res['value']['product_qty'] = th_qty
            res['value']['theoretical_secondqty'] = tot_qty
            res['value']['second_uom'] = tot_qty
        else:
            return super(Batar_inventory_line, self).onchange_createline()
        return res

    @api.multi
    @api.depends("product_id")
    def _get_secondqty(self):
        quant_obj = self.env['stock.quant']
        for line in self:
            # quant_ids = self._get_quants(line)
            quants = quant_obj.search([('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id)])
            # quants = quant_obj.browse(quant_ids)
            tot_qty = sum([x.second_uom for x in quants])
            line.theoretical_secondqty = tot_qty



    @api.model
    def _resolve_inventory_line(self, inventory_line):
        stock_move_obj = self.env['stock.move']
        quant_obj = self.env['stock.quant']
        diff = inventory_line.theoretical_qty - inventory_line.product_qty
        diff_secondqty = inventory_line.theoretical_secondqty - inventory_line.second_uom
        domain = [('qty', '>', 0.0), ('product_id', '=', inventory_line.product_id.id), ('package_id', '=', inventory_line.package_id.id),('lot_id', '=', inventory_line.prod_lot_id.id), ('location_id', '=', inventory_line.location_id.id)]
        quants = quant_obj.search(domain)
        vals = {
            'name': _('INV:') + (inventory_line.inventory_id.name or ''),
            'product_id': inventory_line.product_id.id,
            'product_uom': inventory_line.product_uom_id.id,
            'date': inventory_line.inventory_id.date,
            'company_id': inventory_line.inventory_id.company_id.id,
            'inventory_id': inventory_line.inventory_id.id,
            'state': 'confirmed',
            'restrict_lot_id': inventory_line.prod_lot_id.id,
            'restrict_partner_id': inventory_line.partner_id.id,
         }
        inventory_location_id = inventory_line.product_id.property_stock_inventory.id
        if diff_secondqty == 0:
            res = super(Batar_inventory_line, self)._resolve_inventory_line(inventory_line)
            return res
        elif diff_secondqty > 0:
            vals['location_id'] = inventory_line.location_id.id
            vals['location_dest_id'] = inventory_location_id
            vals['second_uom'] = diff_secondqty
            if diff >= 0:
                vals['product_uom_qty'] = diff
                move_id = stock_move_obj.create(vals)
                quant_id = quant_obj.resolve_move(move_id)
                if quants:
                    quants.history_ids[0].write({
                        'quant_ids': [(4, quant_id.id)]
                    })
                    quants[0].write({
                        'second_uom': inventory_line.second_uom,
                    })
                return move_id
            # if diff < 0:
            #     raise UserError(_('Product error："%s"。') % inventory_line.product_id.name)
                # vals['location_id'] = inventory_location_id
                # vals['location_dest_id'] = inventory_line.location_id.id
                # vals['second_uom'] = 0
                # vals['product_uom_qty'] = -diff
                # move_id2 = stock_move_obj.create(vals)
                # move_id = move_id +  move_id2
                # quant_id = quant_obj.resolve_move(move_id2)
                # quants.history_ids[0].write({
                #     'quant_ids': [(4,quant_id.id)]
                # })
        else:
            vals['location_id'] = inventory_location_id
            vals['location_dest_id'] = inventory_line.location_id.id
            vals['second_uom'] = -diff_secondqty
            # vals['product_uom_qty'] = 0
            if diff < 0:
                vals['product_uom_qty'] = -diff
                move_id = stock_move_obj.create(vals)
                # quant_id = quant_obj.resolve_move(move_id)
                # if quants:
                #     quants.history_ids[0].write({
                #         'quant_ids': [(4, quant_id.id)]
                #     })
                return move_id
            # elif diff > 0:
            #     raise UserError(_('盘点数据有误，增加了负克重的产品："%s"。') % inventory_line.product_id.name)
            else:
                vals['product_uom_qty'] = 0
                move_id = stock_move_obj.create(vals)
                if quants:
                    quants.write({
                        'history_ids': [(4, move_id.id)]
                    })
                    quants[0].write({
                        'second_uom': inventory_line.second_uom,
                    })
                # vals['location_id'] = inventory_line.location_id.id
                # vals['location_dest_id'] = inventory_location_id
                # vals['second_uom'] = 0
                # vals['product_uom_qty'] = diff
                # move_id2 = stock_move_obj.create(vals)
                # move_id = move_id + move_id2
                # quant_id = quant_obj.resolve_move(move_id2)
                # quants.history_ids[0].write({
                #     'quant_ids': [(4, quant_id.id)]
                # })

class Batarquant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def resolve_move(self, move, lot_id=False, owner_id=False):
        quant_obj = self.env['stock.quant']
        price_unit = self.env['stock.move'].get_price_unit(move)
        vals = {
            'product_id': move.product_id.id,
            'location_id': move.location_dest_id.id,
            'qty': move.product_uom_qty,
            'cost': price_unit,
            'history_ids': [(4, move.id)],
            'in_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'company_id': move.company_id.id,
            'lot_id': lot_id,
            'owner_id': owner_id,
            'second_uom': move.second_uom,
            }

        quant_id = quant_obj.create(vals)
        return quant_id

