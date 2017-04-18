# -*- coding: utf-8 -*-

'''
对分拣盘子的管理，前期不管理到具体哪个盘子，只管理到使用盘子的类型，
'''
from openerp import models,  fields,api


class tuo_pan_type(models.Model):
    '''盘子的类型决定了格子数量和总容量'''
    _name = 'tuo.pan.type'
    name = fields.Char(string='name')
    code = fields.Char(string='code')
    volume = fields.Integer(string='Total Volume')
    grid_number = fields.Integer(string='grid number')
    per_volume = fields.Integer(string='per grid volume')
    line_ids = fields.One2many('batar.pick.tuopan','type_id',string='tuo pan type lines')

    @api.multi
    def get_no_use(self):
        ''''''
        picking_list = self.env['batar.pick.tuopan'].search([('type_id', '=', self.id),('used','=',False)])
        action = self.env.ref('batar_mobile_pick.batar_pick_tuopan_action')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }

        pick_ids = [line.id for line in picking_list]

        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        elif len(pick_ids) == 1:
            form = self.env.ref('batar_mobile_pick.batar_pick_tuopan_form', False)
            form_id = form.id if form else False
            result['views'] = [(form_id, 'form')]
            result['res_id'] = pick_ids[0]
        return result

    @api.multi
    def get_used(self):
        ''''''
        picking_list = self.env['batar.pick.tuopan'].search([('type_id', '=', self.id), ('used', '=', True)])
        action = self.env.ref('batar_mobile_pick.batar_pick_tuopan_action')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }

        pick_ids = [line.id for line in picking_list]

        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        elif len(pick_ids) == 1:
            form = self.env.ref('batar_mobile_pick.batar_pick_tuopan_form', False)
            form_id = form.id if form else False
            result['views'] = [(form_id, 'form')]
            result['res_id'] = pick_ids[0]
        return result


class PickTuopan(models.Model):
    _name = 'batar.pick.tuopan'

    type_id = fields.Many2one('tup.pan.type',string='tuo pan type')
    code = fields.Char(string='tuo pan code')
    used = fields.Boolean(string='was used',default=False)

    _sql_constraints = [
        ('code_uniq', 'unique (code)', u'托盘编码必须唯一'),
    ]
