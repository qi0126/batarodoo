# -*- coding: utf-8 -*-
from openerp import api, fields, models

class InternalTrans(models.Model):
    _inherit = 'sample.trans.lines'

    ref = fields.Char(string='Ref')
