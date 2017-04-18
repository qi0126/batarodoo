# -*- coding: utf-8 -*-

from openerp import api, fields, models, exceptions, SUPERUSER_ID
from openerp.exceptions import UserError
from openerp.tools.translate import _
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
import logging
_logger = logging.getLogger(__name__)

class Putaway(models.Model):
    _inherit = 'product.putaway'

    method = fields.Selection([('fixed', 'Fixed Location'), ('dynamic', '自动上架'), ('semi_auto', '部分自动')])

    @api.model
    def prepare_putaway(self, product):
        quant_obj = self.env['stock.quant']
        parent_location = product.product_sample_location.location_id
        res = []
        # view_locs = self.env['stock.location'].search(
        #     [('location_id', '=', parent_location.id), ('usage', '=', 'view')])
        # while parent_location:
            # actual_location = self.env['stock.location'].search(
            #     [('location_id', '=', parent_location.id), ('is_sample', '=', False), ('usage', '=', 'view')])
            # if actual_location.child_ids:
        view_locs = self.env['stock.location'].search(
             [('location_id', '=', parent_location.id), ('usage', '=', 'view')])
        for loc in view_locs:
            if loc.child_ids:
                # for i in actual_location:
                for i in loc.child_ids:
                    total = 0.0
                    for line in quant_obj.search([('location_id', '=', i.id)]):
                        total += line.product_id.product_volume * line.qty
                    if i.location_volume - total >= product.product_volume:
                        res.append(i.id)
                        return i.id
            else:
                raise exceptions.ValidationError('不存托盘库位！')


            # for loc in view_locs:
            #     if loc:
            #         parent_location = loc
            #         view_locs -= loc
            #         break
        if len(res) == 0:
            raise exceptions.ValidationError('所有储柜已满！')

    @api.model
    def putaway_apply(self, putaway_strat, product):
        if putaway_strat.method == 'dynamic':
            quant_obj = self.env['stock.quant']
            if quant_obj.search([('location_id', '=', product.product_sample_location.id), ('product_id', '=', product.id)]):
                loc = self.prepare_putaway(product)
                return loc
            else:
                return product.product_sample_location.id
        elif putaway_strat.method == 'semi_auto':
            loc = self.prepare_putaway(product)
            return loc
            # quant_obj = self.env['stock.quant']
            # if quant_obj.search([('location_id', '=', product.product_sample_location.id), ('product_id', '=', product.id)]):
            #     parent_location = product.product_sample_location.location_id
            #     res = []
            #     view_locs = self.env['stock.location'].search([('location_id', '=', parent_location.id), ('usage', '=', 'view')])
            #     while parent_location:
            #         actual_location = self.env['stock.location'].search(
            #             [('location_id', '=', parent_location.id), ('is_sample', '=', False), ('usage', '=', 'internal')])
            #         if actual_location:
            #             for i in actual_location:
            #                 total = 0.0
            #                 for line in quant_obj.search([('location_id', '=', i.id)]):
            #                     total += line.product_id.product_volume * line.qty
            #                 if i.location_volume - total >= product.product_volume:
            #                     res.append(i.id)
            #                     return i.id
            #         for loc in view_locs:
            #             if loc:
            #                 parent_location = loc
            #                 view_locs -= loc
            #                 break
            #     if len(res) == 0:
            #         raise exceptions.ValidationError('所有储柜已满！')
            # else:
            #     return product.product_sample_location.id
        else:
            return super(Putaway, self).putaway_apply(putaway_strat, product)
        #         actual_location = self.env['stock.location'].search([('location_id', '=', parent_location.id), ('is_sample', '=', False)])
        #         if actual_location:
        #             res = []
        #             for i in actual_location:
        #                 total = 0.0
        #                 for line in quant_obj.search([('location_id', '=', i.id)]):
        #                     total += line.product_id.product_volume * line.qty
        #                 if i.location_volume - total >= product.product_volume:
        #                     res.append(i.id)
        #             if len(res) == 0:
        #                 raise exceptions.ValidationError('所有储柜已满！')
        #             else:
        #                 return res[0]
        #
        #         else:
        #             raise exceptions.ValidationError('%s 没有储柜！' % parent_location.name)
        #     else:
        #         return product.product_sample_location.id
        # else:
        #     return super(Product, self).putaway_apply(putaway_strat, product)


class Product(models.Model):
    _inherit = 'product.product'

    product_volume = fields.Integer(string='Volume', help="the physical location of each product", default=1)
    product_sample_location = fields.Many2one('stock.location', string='Sample Location')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    template_volume = fields.Integer(string='Volume', help="the physical location of each product")

class Location(models.Model):
    _inherit = 'stock.location'
    _order = 'seq_barcode'

    @api.one
    @api.depends('location_volume')
    def _get_availible_volume(self):
        total = 0.0
        quant_obj = self.env['stock.quant']
        for line in quant_obj.search([('location_id', '=', self.id)]):
            total += line.product_id.product_volume * line.qty
        self.availible_volume = self.location_volume - total
    location_volume = fields.Integer(string='Volume', default=1)
    availible_volume = fields.Integer(string='Availible Volume', compute=_get_availible_volume)
    is_sample = fields.Boolean(string='Is sample', default=False)
    seq_barcode = fields.Integer(string='Sequence barcode')

    @api.model
    def create(self, vals):
        if vals.get('barcode'):
            vals['seq_barcode'] = int(vals['barcode'].replace('-', ''))
        res = super(Location, self).create(vals)
        return res
    @api.model
    def auto_set_seqbarcode(self):
        location = self.env['stock.location']
        locs = location.search([('barcode', '!=', False), ('seq_barcode', '=', 0)])
        for loc in locs:
            seq_barcode = int(loc.barcode.replace('-', ''))
            loc.write({'seq_barcode': seq_barcode})
        return True

    @api.model
    def get_putaway_strategy(self, location, product):
        putaway_obj = self.env['product.putaway']
        loc = location
        while loc:
            if loc.putaway_strategy_id:
                res = putaway_obj.putaway_apply(loc.putaway_strategy_id, product)
                if res:
                    return res
            loc = loc.location_id

    @api.model
    def auto_sample_update(self):
        # raise exceptions.ValidationError('Test!')
        quant_obj = self.env['stock.quant']
        sample_location = self.env['stock.location'].search([('is_sample', '=', True)])
        res = self.env['stock.picking']
        internal = self.env['stock.picking.type'].search([('code', '=', 'internal')])
        if sample_location:
            for loc in sample_location:
                noproccess_product = set()
                for i in res.search([('picking_type_id', '=', internal.id), ('location_dest_id', '=', loc.id), ('state', '!=', 'done')]):
                    for line in i.move_lines:
                        noproccess_product.add(line.product_id.id)
                for quant in quant_obj.search([('location_id', '=', loc.id)]):
                    noproccess_product.add(quant.product_id.id)
                parent_location = loc.location_id
                view_locs = self.env['stock.location'].search([('location_id', '=', parent_location.id), ('usage', '=', 'view')])
                while parent_location:
                    stock_location = self.env['stock.location'].search(
                        [('is_sample', '=', False), ('location_id', '=', parent_location.id), ('usage', '=', 'internal')])
                    if stock_location:
                        for stock in stock_location:
                            for stock_quant in quant_obj.search([('location_id', '=', stock.id)]):
                                if stock_quant.product_id.id not in noproccess_product:
                                    vals = {
                                        'product_id': stock_quant.product_id.id,
                                        'location_id': stock.id,
                                        'location_dest_id': loc.id,
                                        'product_uom': stock_quant.product_id.uom_id.id,
                                        'product_uom_qty': 1,
                                        'name': 'auto',

                                    }
                                    # move_id = self.env['stock.move'].create(vals)
                                    picking_vals = {
                                        'location_id': stock.id,
                                        'location_dest_id': loc.id,
                                        'move_lines': [(0, _, vals)],
                                        'picking_type_id': internal.id,
                                    }
                                    res += self.env['stock.picking'].create(picking_vals)
                                    noproccess_product.add(stock_quant.product_id.id)
                                    _logger.info = ('Create Info')
                    if view_locs:
                        for view_loc in view_locs:
                            if view_loc:
                                parent_location = view_loc
                                view_locs -= view_loc
                                break
                    else:
                        break
                # stock_location = self.env['stock.location'].search([('is_sample', '=', False), ('location_id', '=', parent_location.id)])
                # for stock in stock_location:
                #     for stock_quant in quant_obj.search([('location_id', '=', stock.id)]):
                #         if stock_quant.product_id.id not in noproccess_product:
                #             vals = {
                #                 'product_id': stock_quant.product_id.id,
                #                 'location_id': stock.id,
                #                 'location_dest_id': loc.id,
                #                 'product_uom': stock_quant.product_id.uom_id.id,
                #                 'product_uom_qty': 1,
                #                 'name': 'auto',
                #
                #             }
                #             # move_id = self.env['stock.move'].create(vals)
                #             picking_vals = {
                #                 'location_id': stock.id,
                #                 'location_dest_id': loc.id,
                #                 'move_lines': [(0, _, vals)],
                #                 'picking_type_id': internal.id,
                #             }
                #             res += self.env['stock.picking'].create(picking_vals)
                #             noproccess_product.add(stock_quant.product_id.id)
                #             _logger.info = ('Create Info')
            res.action_confirm()
            return res


class stock_pick(models.Model):
    _inherit = 'stock.picking'

    def _prepare_pack_ops(self, cr, uid, picking, quants, forced_qties, context=None):
        """ returns a list of dict, ready to be used in create() of stock.pack.operation.

        :param picking: browse record (stock.picking)
        :param quants: browse record list (stock.quant). List of quants associated to the picking
        :param forced_qties: dictionary showing for each product (keys) its corresponding quantity (value) that is not covered by the quants associated to the picking
        """

        def _picking_putaway_apply(product):
            location = False
            # Search putaway strategy
            if product_putaway_strats.get(product.id):
                location = product_putaway_strats[product.id]
            else:
                location = self.pool.get('stock.location').get_putaway_strategy(cr, uid, picking.location_dest_id, product, context=context)
                product_putaway_strats[product.id] = location
            return location or picking.location_dest_id.id

        # If we encounter an UoM that is smaller than the default UoM or the one already chosen, use the new one instead.
        product_uom = {}  # Determines UoM used in pack operations
        location_dest_id = None
        location_id = None
        for move in [x for x in picking.move_lines if x.state not in ('done', 'cancel')]:
            if not product_uom.get(move.product_id.id):
                product_uom[move.product_id.id] = move.product_id.uom_id
            if move.product_uom.id != move.product_id.uom_id.id and move.product_uom.factor > product_uom[
                move.product_id.id].factor:
                product_uom[move.product_id.id] = move.product_uom
            if not move.scrapped:
                if location_dest_id and move.location_dest_id.id != location_dest_id:
                    #raise UserError(_('The destination location must be the same for all the moves of the picking.'))
                    raise UserError(u'目标库位必须 和移动明细的库位必须一致')
                location_dest_id = move.location_dest_id.id
                if location_id and move.location_id.id != location_id:
                    #raise UserError(_('The source location must be the same for all the moves of the picking.'))
                    raise UserError(u'源库位必须 和移动明细的库位必须一致')
                location_id = move.location_id.id

        pack_obj = self.pool.get("stock.quant.package")
        quant_obj = self.pool.get("stock.quant")
        vals = []
        qtys_grouped = {}
        lots_grouped = {}
        # for each quant of the picking, find the suggested location
        quants_suggested_locations = {}
        product_putaway_strats = {}
        for quant in quants:
            if quant.qty <= 0:
                continue
            suggested_location_id = _picking_putaway_apply(quant.product_id)
            quants_suggested_locations[quant] = suggested_location_id


        # find the packages we can movei as a whole
        top_lvl_packages = self._get_top_level_packages(cr, uid, quants_suggested_locations, context=context)
        # and then create pack operations for the top-level packages found
        for pack in top_lvl_packages:
            pack_quant_ids = pack_obj.get_content(cr, uid, [pack.id], context=context)
            pack_quants = quant_obj.browse(cr, uid, pack_quant_ids, context=context)
            vals.append({
                'picking_id': picking.id,
                'package_id': pack.id,
                'product_qty': 1.0,
                'location_id': pack.location_id.id,
                'location_dest_id': quants_suggested_locations[pack_quants[0]],
                'owner_id': pack.owner_id.id,
            })
            # remove the quants inside the package so that they are excluded from the rest of the computation
            for quant in pack_quants:
                del quants_suggested_locations[quant]
        # Go through all remaining reserved quants and group by product, package, owner, source location and dest location
        # Lots will go into pack operation lot object
        for quant, dest_location_id in quants_suggested_locations.items():
            key = (quant.product_id.id, quant.package_id.id, quant.owner_id.id, quant.location_id.id, dest_location_id)
            if qtys_grouped.get(key):
                qtys_grouped[key] += quant.qty
            else:
                qtys_grouped[key] = quant.qty
            if quant.product_id.tracking != 'none' and quant.lot_id:
                lots_grouped.setdefault(key, {}).setdefault(quant.lot_id.id, 0.0)
                lots_grouped[key][quant.lot_id.id] += quant.qty

        # Do the same for the forced quantities (in cases of force_assign or incomming shipment for example)
        for product, qty in forced_qties.items():
            if qty <= 0:
                continue
            suggested_location_id = _picking_putaway_apply(product)
            key = (product.id, False, picking.owner_id.id, picking.location_id.id, suggested_location_id)
            if qtys_grouped.get(key):
                qtys_grouped[key] += qty
            else:
                qtys_grouped[key] = qty

        # Create the necessary operations for the grouped quants and remaining qtys
        uom_obj = self.pool.get('product.uom')
        prevals = {}
        for key, qty in qtys_grouped.items():
            product = self.pool.get("product.product").browse(cr, uid, key[0], context=context)
            uom_id = product.uom_id.id
            qty_uom = qty
            if product_uom.get(key[0]):
                uom_id = product_uom[key[0]].id
                qty_uom = uom_obj._compute_qty(cr, uid, product.uom_id.id, qty, uom_id)
            pack_lot_ids = []
            if lots_grouped.get(key):
                for lot in lots_grouped[key].keys():
                    pack_lot_ids += [(0, 0, {'lot_id': lot, 'qty': 0.0, 'qty_todo': lots_grouped[key][lot]})]
            val_dict = {
                'picking_id': picking.id,
                'product_qty': qty_uom,
                'product_id': key[0],
                'package_id': key[1],
                'owner_id': key[2],
                'location_id': key[3],
                'location_dest_id': key[4],
                'product_uom_id': uom_id,
                'pack_lot_ids': pack_lot_ids,
            }
            if key[0] in prevals:
                prevals[key[0]].append(val_dict)
            else:
                prevals[key[0]] = [val_dict]
        # prevals var holds the operations in order to create them in the same order than the picking stock moves if possible
        processed_products = set()
        for move in [x for x in picking.move_lines if x.state not in ('done', 'cancel')]:
            if move.product_id.id not in processed_products:
                vals += prevals.get(move.product_id.id, [])
                processed_products.add(move.product_id.id)
        return vals

class stock_move(models.Model):
    _inherit = 'stock.move'

    second_uom = fields.Float(string='Second uom')


class stock_quant(models.Model):
    _inherit = 'stock.quant'

    second_uom = fields.Float(string='Second uom')
    parent_location = fields.Many2one('stock.location', string='Parent location', related='location_id.location_id', store=True)

    def _quant_create(self, cr, uid, qty, move, lot_id=False, owner_id=False, src_package_id=False,
                      dest_package_id=False,
                      force_location_from=False, force_location_to=False, context=None):


        '''Create a quant in the destination location and create a negative quant in the source location if it's an internal location.
        '''
        if context is None:
            context = {}
        price_unit = self.pool.get('stock.move').get_price_unit(cr, uid, move, context=context)
        location = force_location_to or move.location_dest_id
        rounding = move.product_id.uom_id.rounding
        vals = {
            'product_id': move.product_id.id,
            'location_id': location.id,
            'qty': float_round(qty, precision_rounding=rounding),
            'cost': price_unit,
            'history_ids': [(4, move.id)],
            'in_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'company_id': move.company_id.id,
            'lot_id': lot_id,
            'owner_id': owner_id,
            'package_id': dest_package_id,
            'second_uom': move.second_uom,
        }
        if move.location_id.usage == 'internal':
            # if we were trying to move something from an internal location and reach here (quant creation),
            # it means that a negative quant has to be created as well.
            negative_vals = vals.copy()
            negative_vals['location_id'] = force_location_from and force_location_from.id or move.location_id.id
            negative_vals['qty'] = float_round(-qty, precision_rounding=rounding)
            negative_vals['cost'] = price_unit
            negative_vals['second_uom'] = float_round(-move.second_uom, precision_rounding=rounding)
            negative_vals['negative_move_id'] = move.id
            negative_vals['package_id'] = src_package_id
            negative_quant_id = self.create(cr, SUPERUSER_ID, negative_vals, context=context)
            vals.update({'propagated_from_id': negative_quant_id})

        # In case of serial tracking, check if the product does not exist somewhere internally already
        picking_type = move.picking_id and move.picking_id.picking_type_id or False
        if lot_id and move.product_id.tracking == 'serial' and (
            not picking_type or (picking_type.use_create_lots or picking_type.use_existing_lots)):
            if qty != 1.0:
                #raise UserError(_('You should only receive by the piece with the same serial number'))
                raise UserError(u'序列号相同的才可以接收，请联系管理员')
            other_quants = self.search(cr, uid, [('product_id', '=', move.product_id.id), ('lot_id', '=', lot_id),
                                                 ('qty', '>', 0.0), ('location_id.usage', '=', 'internal')], context=context)
            if other_quants:
                lot_name = self.pool['stock.production.lot'].browse(cr, uid, lot_id, context=context).name
                raise UserError(u"序列号%s已经存在" % lot_name + u"请确认库位或者拥有者是否已经设置")
#                 raise UserError(_('The serial number %s is already in stock.') % lot_name + _(
#                     "Otherwise make sure the right stock/owner is set."))

        # create the quant as superuser, because we want to restrict the creation of quant manually: we should always use this method to create quants
        quant_id = self.create(cr, SUPERUSER_ID, vals, context=context)
        return self.browse(cr, uid, quant_id, context=context)