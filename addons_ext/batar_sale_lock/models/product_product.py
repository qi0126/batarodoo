# -*- coding: utf-8 -*-
'''
Created on 2016年7月1日
修改库存插叙方式，在草稿状态下即进行锁库
@author: cloudy
'''
from openerp.osv import fields, osv
from openerp.tools.float_utils import float_round
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF
from datetime import datetime, timedelta
import pytz

localtz = pytz.timezone('Asia/Shanghai')

class product_product(osv.osv):
    _inherit ='product.product'
    _order ="has_stock desc"


    def _has_compute(self, cr, uid, ids, context):
        '''判断是否有可售库存'''
        res= {}
        products = self.pool.get('product.product').browse(cr,uid,ids,context)
        for product in products:
            if product.virtual_available > 0:
                res[product.id]['has_stock'] = True
            else:
                res[product.id]['has_stock']= False



    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        context = context or {}
        field_names = field_names or []

        domain_products = [('product_id', 'in', ids)]
        domain_quant, domain_move_in, domain_move_out = [], [], []
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations(cr, uid, ids, context=context)
        domain_move_in += self._get_domain_dates(cr, uid, ids, context=context) + [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_products
        domain_move_out += self._get_domain_dates(cr, uid, ids, context=context) + [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_products
        domain_quant += domain_products

        if context.get('lot_id'):
            domain_quant.append(('lot_id', '=', context['lot_id']))
        if context.get('owner_id'):
            domain_quant.append(('owner_id', '=', context['owner_id']))
            owner_domain = ('restrict_partner_id', '=', context['owner_id'])
            domain_move_in.append(owner_domain)
            domain_move_out.append(owner_domain)
        if context.get('package_id'):
            domain_quant.append(('package_id', '=', context['package_id']))

        domain_move_in += domain_move_in_loc
        domain_move_out += domain_move_out_loc
        moves_in = self.pool.get('stock.move').read_group(cr, uid, domain_move_in, ['product_id', 'product_qty'], ['product_id'], context=context)
        moves_out = self.pool.get('stock.move').read_group(cr, uid, domain_move_out, ['product_id', 'product_qty'], ['product_id'], context=context)

        domain_quant += domain_quant_loc
        quants = self.pool.get('stock.quant').read_group(cr, uid, domain_quant, ['product_id', 'qty'], ['product_id'], context=context)
        quants = dict(map(lambda x: (x['product_id'][0], x['qty']), quants))

        moves_in = dict(map(lambda x: (x['product_id'][0], x['product_qty']), moves_in))
        moves_out = dict(map(lambda x: (x['product_id'][0], x['product_qty']), moves_out))
        res = {}
        ctx = context.copy()
        ctx.update({'prefetch_fields': False})
        for product in self.browse(cr, uid, ids, context=ctx):
            id = product.id
            qty_available = float_round(quants.get(id, 0.0), precision_rounding=product.uom_id.rounding)
            incoming_qty = float_round(moves_in.get(id, 0.0), precision_rounding=product.uom_id.rounding)
            outgoing_qty = float_round(moves_out.get(id, 0.0), precision_rounding=product.uom_id.rounding)
            virtual_available = float_round(quants.get(id, 0.0) + moves_in.get(id, 0.0) - moves_out.get(id, 0.0), precision_rounding=product.uom_id.rounding)
            res[id] = {
                'qty_available': qty_available,
                'incoming_qty': incoming_qty,
                'outgoing_qty': outgoing_qty,
                'virtual_available': virtual_available,
            }
            add_line_ids = self.pool.get('stock.pick.add.line').search(cr,uid,[('state','in',('draft','confirm')),('product_id','=',id)])
            add_lines = self.pool.get('stock.pick.add.line').browse(cr,uid,add_line_ids)
            for add_line in add_lines:
                res[id]['virtual_available'] -= add_line.product_qty
        #查询草稿状态且为两个小时内的订单
        config_id = self.pool.get('sale.config.settings').search(cr,uid,[],limit=1,order='id desc')
        config_id = config_id and config_id[0]
        hours = 2
        if  config_id:
            hours = self.pool.get('sale.config.settings').browse(cr,uid,config_id,context=context).lock_time
        now = datetime.now(localtz)+timedelta(hours=-(hours+8))
        update_time = now.strftime(DF)
        
        sale_orders_ids = self.pool.get('sale.order').search(cr, uid,[('state','=','draft'),('write_date','>',update_time)])
        #batar_customer_sale =self.pool.get('batar.customer.sale').search(cr,uid,[('state','=','process'),('write_date','>',update_time)])
        # customer_sale_ids = [line.id for line in batar_customer_sale]
        need_lock_product_ids = res.keys()
        for lock_id in need_lock_product_ids:
            order_line_ids = self.pool.get('sale.order.line').search(cr, uid,[('order_id','in',sale_orders_ids),('product_id','=',lock_id),('state','=','draft')])
            order_lines = self.pool.get('sale.order.line').browse(cr,uid ,order_line_ids,context=context)
            sum = 0.0
            customer_sale_line_ids = self.pool.get('customer.sale.line').search(cr,uid,[('product_id','=',lock_id),('change_qty','>',0)])
            if customer_sale_line_ids:
                customer_sale_lines = self.pool.get('customer.sale.line').browse(cr,uid ,customer_sale_line_ids,context=context)
                for sale_line in customer_sale_lines:
                    sum += sale_line.change_qty
            for order_line in order_lines:
                sum += order_line.product_uom_qty
            res[lock_id]['qty_available'] -= float(sum)
            res[lock_id]['virtual_available'] -= sum
        for p in self.browse(cr, uid, ids, context=ctx):
            id = p.id
            if res[id]['virtual_available'] > 0:
                self.write(cr, uid, [id], {'has_stock': True}, context=ctx)
            else:
                self.write(cr, uid, [id], {'has_stock': False}, context=ctx)

        return res
    def _search_product_quantity(self, cr, uid, obj, name, domain, context):
        res = []
        for field, operator, value in domain:
            #to prevent sql injections
            assert field in ('qty_available', 'virtual_available', 'incoming_qty', 'outgoing_qty'), 'Invalid domain left operand'
            assert operator in ('<', '>', '=', '!=', '<=', '>='), 'Invalid domain operator'
            assert isinstance(value, (float, int)), 'Invalid domain right operand'

            if operator == '=':
                operator = '=='

            ids = []
            if name == 'qty_available' and (value != 0.0 or operator not in  ('==', '>=', '<=')):
                res.append(('id', 'in', self._search_qty_available(cr, uid, operator, value, context)))
            else:
                product_ids = self.search(cr, uid, [], context=context)
                if product_ids:
                    #TODO: Still optimization possible when searching virtual quantities
                    for element in self.browse(cr, uid, product_ids, context=context):
                        if eval(str(element[field]) + operator + str(value)):
                            ids.append(element.id)
                    res.append(('id', 'in', ids))
        return res
    _columns = {
        'qty_available': fields.function(_product_available, multi='qty_available',
            type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quantity On Hand',
            fnct_search=_search_product_quantity,
            help="Current quantity of products.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "with 'internal' type."),
        'virtual_available': fields.function(_product_available, multi='qty_available',
            type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Forecast Quantity',
            fnct_search=_search_product_quantity,
            help="Forecast quantity (computed as Quantity On Hand "
                 "- Outgoing + Incoming)\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored in this location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "with 'internal' type."),
        'incoming_qty': fields.function(_product_available, multi='qty_available',
            type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Incoming',
            fnct_search=_search_product_quantity,
            help="Quantity of products that are planned to arrive.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods arriving to this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods arriving to the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "Otherwise, this includes goods arriving to any Stock "
                 "Location with 'internal' type."),
        'outgoing_qty': fields.function(_product_available, multi='qty_available',
            type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Outgoing',
            fnct_search=_search_product_quantity,
            help="Quantity of products that are planned to leave.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods leaving this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods leaving the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "Otherwise, this includes goods leaving any Stock "
                 "Location with 'internal' type."),
        'has_stock':fields.boolean(string='has stock',index=True)
        }
    
    