# -*- coding: utf-8 -*-
'''
Created on 2016年3月17日

@author: cloudy
'''

from openerp import models,fields,api
import math


class account_tax(models.Model):
    _inherit = 'account.tax'

    #如果all_weights为0且ponderable为真 表示商品还未称量
    #ponderable为假 表示商品为按件销售
    #ponderable为真且all_weights不为零表示商品已经称量
    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None,ponderable=False,real_time_price_unit=0,item_fee=0,weight_fee=0,standard_weight=0,all_weights=0):
        """ Returns the amount of a single tax. base_amount is the actual amount on which the tax is applied, which is
            price_unit * quantity eventually affected by previous taxes (if tax is include_base_amount XOR price_include)
        """
        
        self.ensure_one()
        if self.amount_type == 'fixed':
            return math.copysign(self.amount, base_amount) * quantity
        if (self.amount_type == 'percent' and not self.price_include) or (self.amount_type == 'division' and self.price_include):
            return base_amount * self.amount / 100
        if self.amount_type == 'percent' and self.price_include:
            return base_amount - (base_amount / (1 + self.amount / 100))
        if self.amount_type == 'division' and not self.price_include:
            return base_amount / (1 - self.amount / 100) - base_amount
        
    @api.v8
    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None,ponderable=False,real_time_price_unit=0,item_fee=0,weight_fee=0,standard_weight=0,all_weights=0):
        """在原有函数的基础上增加重量，金价附加费等信息
         Returns all information required to apply taxes (in self + their children in case of a tax goup).
            We consider the sequence of the parent for group of taxes.
                Eg. considering letters as taxes and alphabetic order as sequence :
                [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]

        RETURN: {
            'total_excluded': 0.0,    # Total without taxes
            'total_included': 0.0,    # Total with taxes
            'taxes': [{               # One dict for each tax in self and their children
                'id': int,
                'name': str,
                'amount': float,
                'sequence': int,
                'account_id': int,
                'refund_account_id': int,
                'analytic': boolean,
            }]
        } """
        '''如果产品不为可称量，则为按件卖，只需要考虑件附加费'''
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        taxes = []
        # By default, for each tax, tax amount will first be computed
        # and rounded at the 'Account' decimal precision for each
        # PO/SO/invoice line and then these rounded amounts will be
        # summed, leading to the total amount for that tax. But, if the
        # company has tax_calculation_rounding_method = round_globally,
        # we still follow the same method, but we use a much larger
        # precision when we round the tax amount for each line (we use
        # the 'Account' decimal precision + 5), and that way it's like
        # rounding after the sum of the tax amounts of each line
        prec = currency.decimal_places
        if company_id.tax_calculation_rounding_method == 'round_globally':
            prec += 5
        #为了保证变量有不去除改行
        total_excluded = total_included = base = round(price_unit * quantity, prec)
        #根据商品是否可称量，商品是否称重计算金额
        #可称量
        if ponderable:
            #若已经称量
            if all_weights:
                #称重重量*(实时金价+工费)+(数量*件附加费)
                round_money = all_weights*(real_time_price_unit+weight_fee) + quantity*item_fee
                total_excluded = total_included = base = round(round_money, prec)
            #没有称量
            else:
                #标准重量*数量*(实时金价+工费)+(数量*件附加费)，其中工费包括基本工费和附加工费
                round_money = standard_weight * quantity*(real_time_price_unit+weight_fee) + quantity*item_fee
                total_excluded = total_included = base = round(round_money, prec)
        #按件销售
        else:
            #若按件销售，需要将件附加费计算进去
            total_excluded = total_included = base = round((price_unit+ item_fee)* quantity, prec)
            
        for tax in self:
            #税组
            if tax.amount_type == 'group':
                ret = tax.children_tax_ids.compute_all(price_unit, currency, quantity, product, partner,ponderable,real_time_price_unit,item_fee,standard_weight)
                total_excluded = ret['total_excluded']
                base = ret['base']
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                taxes += ret['taxes']
                continue

            tax_amount = tax._compute_amount(base, price_unit, quantity, product, partner,ponderable,real_time_price_unit,item_fee,weight_fee,standard_weight)
            if company_id.tax_calculation_rounding_method == 'round_globally':
                tax_amount = round(tax_amount, prec)
            else:
                tax_amount = currency.round(tax_amount)

            if tax.price_include:
                total_excluded -= tax_amount
                base -= tax_amount
            else:
                total_included += tax_amount

            if tax.include_base_amount:
                base += tax_amount

            taxes.append({
                'id': tax.id,
                'name': tax.name,
                'amount': tax_amount,
                'sequence': tax.sequence,
                'account_id': tax.account_id.id,
                'refund_account_id': tax.refund_account_id.id,
                'analytic': tax.analytic,
            })

        return {
            'taxes': sorted(taxes, key=lambda k: k['sequence']),
            'total_excluded': currency.round(total_excluded),
            'total_included': currency.round(total_included),
            'base': base,
        }