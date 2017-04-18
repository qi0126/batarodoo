# -*- coding: utf-8 -*-
from openerp import api, models, fields

class User(models.Model):
    _inherit = 'res.users'

    session_id = fields.Char(string='Current Session')