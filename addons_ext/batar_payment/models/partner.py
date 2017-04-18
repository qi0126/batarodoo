# -*- coding: utf-8 -*-
from openerp import api, models, fields
import openerp.addons.decimal_precision as dp

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _compute_total(self):
            for partner in self:
                res = self.env['batar.lailiao'].search([('partner_id', '=', partner.id)])
                debit_total = sum(i.debit for i in res)
                credit_total = sum(i.credit for i in res)
                total = debit_total - credit_total
                partner.compute_total = total
            return True

    lailiao = fields.Boolean(string='Lailiao', default=False)
    lailiao_account = fields.Many2one('account.account', string="Lailiao account")
    compute_total = fields.Float(compute=_compute_total, digits=dp.get_precision('Lai liao'))

#    @api.model
#    def create(self, vals):
#        if self.lailiao:
#            name = 'Test'  + '-' + vals.get('name')
#            code = '1413' + self.env['ir.sequence'].next_by_code('lailiao_account')
#            type = self.env.ref('account.data_account_type_payable')
#            account_id = self.env['account.account'].create({'name': name, 'code': code, 'user_type_id': type, 'reconcile': True})
#            vals['lailiao_account'] = account_id
#            res = super(Partner, self).create(vals)
#            return res


