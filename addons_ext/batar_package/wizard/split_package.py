# -*- coding: utf-8 -*-
from openerp import api, fields, models

class SplitPackage(models.TransientModel):
    _name = 'batar.split.package'

    qty = fields.Integer(string='Split Qty', required=True)
    weight = fields.Float(string='Weight')
    net_weight = fields.Float(string='Net weight')

    @api.multi
    def confirm(self):
        self.ensure_one()
        package_obj = self.env['batar.package']
        package = package_obj.browse(self._context.get('active_ids'))[0]
        balance = package.qty - self.qty
        package.write({'qty': balance})
        package.copy({'qty': self.qty, 'weight': self.weight, 'net_weight': self.net_weight,})
        # vals = {
        #     'qty': self.qty,
        #     'weight': self.weight,
        #     'net_weight': self.net_weight,
        #     'product_id': package.product_id.id,
        #     'partner_id': package.partner_id.id,
        # }
        # package_obj.create(vals)
        return True