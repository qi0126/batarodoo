# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.exceptions import UserError
class Batarsample(models.Model):
    _inherit = 'batar.location.adjustment'

    @api.multi
    def output_sample(self):
        self.ensure_one()
        # if not self.location_id.is_sample:
        #     raise UserError(u'此操作的库位必须是样品库！')
        # else:
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'batar.samplemove.wizard',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('batar_samplemove.batar_samplemove_wizard_form').id,
            'target': 'new',
        }
    @api.multi
    def input_sample(self):
        self.ensure_one()
        if not self.location_id.is_sample:
            raise UserError(u'此操作的库位必须是样品库！')
        else:
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'batar.samplemove.wizard',
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref('batar_samplemove.batar_samplemovein_wizard_form').id,
                'target': 'new',
            }