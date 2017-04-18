# -*- coding: utf-8 -*-
from openerp import fields, api, models
from openerp.exceptions import UserError, Warning

class MultiLocation(models.TransientModel):
    _name = 'batar.multi.location'

    location_id = fields.Many2one('stock.location', string='Location', required=True)
    volume = fields.Integer(string='Volume', help='the volume of each location')
    location_volume = fields.Integer(string='Location volume', compute='get_location_volume')

    @api.depends('location_id')
    def get_location_volume(self):
        if self.location_id:
            self.location_volume = self.location_id.location_volume

    @api.multi
    def confirm(self):
        self.ensure_one()
        location_obj = self.env['stock.location']
        code = self.location_id.barcode.split('-', 1)
        if not self.location_id or self.volume == 0:
            raise UserError(u'没有库位或指定容量值')
        else:
            total_volume = self.location_id.location_volume
            if self.volume > total_volume:
                raise UserError(u'指定容量值不能大于总容量值')
            nums = divmod(total_volume, self.volume)
            if nums[1] != 0:
                raise UserError(u'指定容量值必须被总容量值整除')
            for i in range(1, (nums[0] + 1)):
                vals = {
                    'name': code[0] + '-' + str(i).zfill(len(str(nums[0]))),
                    'location_id': self.location_id.id,
                    'location_volume': self.volume,
                    'barcode': code[0] + '-' + str(i).zfill(len(str(nums[0]))),
                }
                location_obj.create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.location',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('stock.view_location_tree2').id,
            'target': 'current',
            'domain': [('location_id', '=', self.location_id.id)],
        }

    @api.onchange('location_id')
    def onchange_location(self):
        if self.location_id:
            if self.location_id.child_ids:
                return {
                    'warning': {
                        'title': u'提示',
                        'message': u'该托盘已有子库位！',
                    }
                }


    @api.multi
    def reopen_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'context': self._context,
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }