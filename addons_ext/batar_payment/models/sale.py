# -*- coding: utf-8 -*-
from openerp import fields, api, models
import openerp.addons.decimal_precision as dp

class Batar_sale_Order(models.Model):
    _inherit = 'sale.order'

    @api.one
    @api.depends('partner_id')
    def _get_customer_lailiao_total(self):
        if self.partner_id:
            res = self.env['batar.lailiao'].search([('partner_id', '=', self.partner_id.id)])
            debit_total = sum(i.debit for i in res)
            credit_total =sum(i.credit for i in res)
            total = debit_total - credit_total
            self.lailiao_total = total
            return True
    @api.depends('lailiao_payment', 'lailiao_total', 'order_line.price_total')
    def _amount_all(self):
        """
        重新定义销售订单总额计算方式，如果使用存欠支付，扣除所有产品的重量之后，在进行计算加工费
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                if self.lailiao_payment:
                    amount_untaxed += line.cost_subtotal
                    amount_tax += line.cost_tax

                else:
                    amount_untaxed += line.cost_subtotal + line.price_subtotal
                    amount_tax += line.cost_tax + line.price_tax
        order.update({'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                      'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                      'amount_total': amount_untaxed + amount_tax,
                      })


    lailiao_payment = fields.Boolean(string="Batar payment", default=True, help="deduction lailiao", readonly=True, states={'draft': [('readonly', False)]})
    lailiao_total = fields.Float(string="lailiao total", compute=_get_customer_lailiao_total, help="Positive for material stock, negative to owe")



    @api.multi
    def action_confirm(self):
        for order in self:
            order.state = 'sale'
            if self.env.context.get('send_email'):
                self.force_quotation_send()
            order.order_line._action_procurement_create()
            lailiao_docs = self.env['batar.lailiao']
            vals = {}
            vals['partner_id'] = order.partner_id.id
            vals['sale_id'] = order.id
            if order.lailiao_payment:
                qty = sum(i.product_uom_qty for i in order.order_line)
                vals['credit'] = qty
                lailiao_docs = self.env['batar.lailiao'].create(vals)
                return lailiao_docs
            if not order.project_id:
                for line in order.order_line:
                    if line.product_id.invoice_policy == 'cost':
                        order._create_analytic_account()
                        break
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()




class Batar_sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'price_process', 'tax_id')
    def _compute_cost_total(self):
        """
        计算加工费用的总额及税额
        """
        for line in self:
            total = line.tax_id.compute_all(line.price_process, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({'cost_total': total['total_included'],
                         'cost_subtotal': total['total_excluded'],
                         'cost_tax': total['total_included'] - total['total_excluded']
                         })


    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'lailiao_payment')
    def _compute_amount(self):
        """
        重新计算明细行的小计.
        """
        for line in self:
            total = line.tax_id.compute_all(line.price_process, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_id)
            if line.lailiao_payment:
                line.update({'price_total': total['total_included'],
                             'price_subtotal': total['total_excluded'],
                             'price_tax': total['total_included'] - total['total_excluded']
                             })
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id,
                                                partner=line.order_id.partner_id)
                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'] + total['total_included'] - total['total_excluded'],
                    'price_total': taxes['total_included'] + total['total_included'],
                    'price_subtotal': taxes['total_excluded'] + total['total_excluded'],
                })


    price_process = fields.Float(string='Base cost', related='product_id.process_cost', default=0.0)
    cost_total = fields.Float(string='cost total', digits=dp.get_precision('Product Price'), compute=_compute_cost_total)
    cost_subtotal = fields.Float(string='Cost subtotal', digits=dp.get_precision('Product Price'), compute=_compute_cost_total)
    cost_tax = fields.Float(string='Cost tax', digits=dp.get_precision('Product Price'), compute=_compute_cost_total)
    lailiao_payment = fields.Boolean(related='order_id.lailiao_payment', readonly=True)


#    @api.onchange('product_id')
#    def price_process_onchange(self):
#        """
#        根据产品获得基础工费
#        """
#        if self.product_id:
#            self.price_process = self.product_id.process_cost
#            return True