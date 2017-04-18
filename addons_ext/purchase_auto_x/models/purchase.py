# -*- coding: utf-8 -*-
from openerp import api, fields, models
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class Product(models.Model):
    _inherit = 'product.product'

    def _select_seller(self, cr, uid, product_id, partner_id=False, quantity=0.0,
                       date=time.strftime(DEFAULT_SERVER_DATE_FORMAT), uom_id=False, context=None):
        if context is None:
            context = {}
        res = {}
        if product_id.supplier_info:
            res = self.pool.get('product.supplier').browse(cr, uid, [])
            for seller in product_id.supplier_info:
                # Set quantity in UoM of seller
                quantity_uom_seller = quantity
                if quantity_uom_seller and uom_id and uom_id != seller.product_uom:
                    quantity_uom_seller = uom_id._compute_qty_obj(uom_id, quantity_uom_seller, seller.product_uom)
                if partner_id and seller.name not in [partner_id, partner_id.parent_id]:
                    continue

                if seller.product_id and seller.product_id != product_id:
                    continue
                res |= seller
                break
        else:
            res = super(Product, self)._select_seller(product_id=product_id, partner_id=partner_id, quantity=quantity, date=time.strftime(DEFAULT_SERVER_DATE_FORMAT), uom_id=uom_id, context=context)
        return res

class Procurement(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def make_po(self):
        res = []
        cache = {}
        if all(procurement.product_id.supplier_info for procurement in self):
            for procurement in self:
                supplier = procurement.product_id.supplier_info[0]
                partner = supplier.name

                gpo = procurement.rule_id.group_propagation_option
                group = (gpo == 'fixed' and procurement.rule_id.group_id) or \
                        (gpo == 'propagate' and procurement.group_id) or False

                domain = (
                    ('partner_id', '=', partner.id),
                    ('state', '=', 'draft'),
                    ('picking_type_id', '=', procurement.rule_id.picking_type_id.id),
                    ('company_id', '=', procurement.company_id.id),
                    ('dest_address_id', '=', procurement.partner_dest_id.id))
                if group:
                    domain += (('group_id', '=', group.id),)

                if domain in cache:
                    po = cache[domain]
                else:
                    po = self.env['purchase.order'].search([dom for dom in domain])
                    po = po[0] if po else False
                    cache[domain] = po
                if not po:
                    vals = procurement._prepare_purchase_order(partner)
                    po = self.env['purchase.order'].create(vals)
                    cache[domain] = po
                elif not po.origin or procurement.origin not in po.origin.split(', '):
                    # Keep track of all procurements
                    if po.origin:
                        if procurement.origin:
                            po.write({'origin': po.origin + ', ' + procurement.origin})
                        else:
                            po.write({'origin': po.origin})
                    else:
                        po.write({'origin': procurement.origin})
                if po:
                    res += [procurement.id]

                # Create Line
                po_line = False
                for line in po.order_line:
                    if line.product_id == procurement.product_id and line.product_uom == procurement.product_id.uom_po_id:
                        procurement_uom_po_qty = self.env['product.uom']._compute_qty_obj(procurement.product_uom,
                                                                                          procurement.product_qty,
                                                                                          procurement.product_id.uom_po_id)
                        seller = self.product_id._select_seller(
                            procurement.product_id,
                            partner_id=partner,
                            quantity=line.product_qty + procurement_uom_po_qty,
                            date=po.date_order and po.date_order[:10],
                            uom_id=procurement.product_id.uom_po_id)

                        price_unit = self.env['account.tax']._fix_tax_included_price(seller.price,
                                                                                     line.product_id.supplier_taxes_id,
                                                                                     line.taxes_id) if seller else 0.0
                        if price_unit and seller and po.currency_id and seller.currency_id != po.currency_id:
                            price_unit = seller.currency_id.compute(price_unit, po.currency_id)

                        po_line = line.write({
                            'product_qty': line.product_qty + procurement_uom_po_qty,
                            'price_unit': price_unit,
                            'procurement_ids': [(4, procurement.id)]
                        })
                        break
                if not po_line:
                    vals = procurement._prepare_purchase_order_line(po, supplier)
                    self.env['purchase.order.line'].create(vals)
        else:
            res = super(Procurement, self).make_po()
        return res