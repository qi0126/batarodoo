# -*- coding: utf-8 -*-
from openerp import api, fields, models, exceptions

class ProductManage(models.Model):
    _name = 'product.manage'
    _inherit = ['ir.needaction_mixin']

    name = fields.Char(string='Name', readonly=True, states={'draft': [('readonly', False)]}, required=True, default='/')
    user_id = fields.Many2one('res.users', string='Manage User', default=lambda self:self.env.uid, readonly=True)
    line_ids = fields.One2many('product.manage.line', 'order_id', string='Product line', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('process', 'Process'), ('done', 'Done')], string='State', default='draft')
    _sql_constraints = [('name_uniq', 'unique (name)', u'名称必须唯一!')]

    @api.model
    def create(self, vals):
        if self.search([('user_id', '=', self.env.uid), ('state', '=', 'draft')]):
            raise exceptions.ValidationError(u'当前用户有未完成的产品维护单！')
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('product_manage') or '/'
        res = super(ProductManage, self).create(vals)
        return res

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]

    @api.multi
    def prepare_product(self):
        self.ensure_one()
        return {
            'view_mode': 'form',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_model': 'product.manage.wizard',
            'view_id': self.env.ref('product_manage_x.product_manage_wizard_form').id,
        }
    @api.multi
    def active_fasle(self):
        self.ensure_one()
        if self.line_ids:
            self.line_ids.mapped('product_id').write({'active': False})
            return self.write({'state': 'done'})
        else:
            raise exceptions.UserError(u'无产品信息')

class ProductLines(models.Model):
    _name = 'product.manage.line'

    order_id = fields.Many2one('product.manage', string='Product Manage', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    uom_id = fields.Many2one(related='product_id.uom_id', string='Uom')
    qty = fields.Float(string='Qty')
    percent = fields.Float(string='Percent')
