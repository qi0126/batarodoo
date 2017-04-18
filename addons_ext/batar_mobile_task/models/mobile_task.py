# -*- coding: utf-8 -*-
from openerp import api, fields, models

class MobileTask(models.Model):
    _name = 'batar.mobile.task'

    @api.model
    def get_task(self):
        input_obj = self.env['batar.input.mobile']
        pick_obj = self.env['batar.mobile.picking']
        res = input_obj.get_input_task()
        res['type'] = 'input'
        if res['code'] == '500':
            res = pick_obj.get_pick_task()
            res['type'] = 'pick'
        return res
