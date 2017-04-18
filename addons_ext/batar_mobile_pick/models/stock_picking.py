# -*- coding: utf-8 -*-
from openerp import models, fields,api

class StockPick(models.Model):
    _inherit = 'stock.picking'

    sample_location = fields.Many2one('stock.location', string='Sample Location')
    mobile_user = fields.Many2one('res.users', string='Pick user')
    # mobile_pick = fields.Many2one('batar.mobile.pick', string='Mobile Pick')

    @api.multi
    @api.onchange('pack_operation_product_ids')
    def onchange_sample_location(self):
        """
        根据操作明细行中产品的样品库来改变整个分拣单的样品库
        """
        for line in self:
            if line.pack_operation_product_ids:
                self.sample_location = line.pack_operation_product_ids[0].product_id.product_sample_location