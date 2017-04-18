# -*- coding: utf-8 -*-
from openerp import api, fields, models, exceptions
import datetime
from openerp import tools
class ProductWizard(models.TransientModel):
    _name = 'product.manage.wizard'

    type = fields.Selection([('month', 'Month'), ('quarter', 'Quarter'), ('year', 'Year'), ('customer', 'Customer')],
                            string='Type', default='month', help="""
                            * 月份（Month）: 30天内，
                            * 季度（Quarter）: 当前季度，如果本月是当前季度的第一个月份，则计算上个季度，
                            * 年度（Year）: 本年度，如果本月是本年度的第一个月份，则计算上年度，
                            * 自定义（Customer）: 自定义时间段，
                            """)
    percent = fields.Float(string='Percent', required=True)
    start_date = fields.Date(string='Start Date', required_if_type='customer')
    end_date = fields.Date(string='End Date', required_if_type='customer')
    line_ids = fields.One2many('product.manage.wizard.line', 'order_id', string='Product Lines')

    # @api.multi
    # def _check_required_type(self):
    #     for line in self:
    #         if any(getattr(f, 'required_if_type', None) == line.type and not line[k] for k, f in self._fields.items()):
    #             return False
    #         else:
    #             return True
    # _constraints = [(_check_required_type, u'起止时间必须填写', ['required for type'])]

    def get_lines(self, start_date, end_date):
        #根据起止时间，计算销量
        res = []
        lines = []
        pick_obj = self.env['stock.picking']
        pick_type = self.env['stock.picking.type'].with_context(lang='en').search([('name', 'ilike', 'Delivery Orders')],limit=1).id
        pick_done = pick_obj.search(
            [('create_date', '>=', start_date), ('create_date', '<=', end_date),
             ('state', '=', 'done'), ('picking_type_id', '=', pick_type)])
        op_done = pick_done.mapped('pack_operation_product_ids')
        total = sum([a.qty_done for a in op_done])
        for p in op_done.mapped('product_id').filtered(lambda x: x.active == True):
            # 计算所有规格产品的出库量，出库总数
            p_done = op_done.filtered(lambda x: x.product_id == p)
            p_total = sum([a.qty_done for a in p_done])
            p_percent = round(p_total / total, 4)
            if p_percent < self.percent / 100:
                res.append((p_percent, p_total, p))
        if res:
            #销售量占比升序
            res.sort(key=lambda x: x[0])
            for product in res:
                vals = {
                    'product_id': product[2].id,
                    'qty': product[1],
                    'product_percent': round(product[0] * 100, 2),
                }
                lines.append((0, 0, vals))
        nosale = self.env['product.product'].search([]) - op_done.mapped('product_id')
        for no_product in nosale:
            vals = {
                'product_id': no_product.id,
                'qty': 0.0,
                'product_percent': 0.0,
            }
            lines.append((0, 0, vals))
        return lines

    @api.multi
    def add_product(self):
        self.ensure_one()
        if self.line_ids:
            self.line_ids.unlink()
        now = datetime.datetime.now()
        year = now.strftime('%Y')
        start_date = None
        end_date = None
        if self.type == 'month':
            #计算30天内，每个产品的销量，并列出小于预设percent
            start_date = (now - datetime.timedelta(days=30)).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
            end_date = now.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        elif self.type == 'quarter':
            # 计算本季度的销售量，如果本月是当前季度的第一个月，则计算上个季度
            q1 = ['01', '02', '03']
            q2 = ['04', '05', '06']
            q3 = ['07', '08', '09']
            q4 = ['10', '11', '12']
            end_date = now.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
            if now.strftime('%m') in q1:
                if now.strftime('%m') == '01':
                    #计算上一年最后一个季度的销量
                    pre_year = str(int(year) - 1)
                    start_date = "%s-10-01 00:00:00" % pre_year
                    end_date = "%s-12-31 23:59:59" % pre_year
                else:
                    start_date = "%s-01-01 00:00:00" % year
            elif now.strftime('%m') in q2:
                if now.strftime('%m') == '04':
                    start_date = "%s-01-01 00:00:00" % year
                    end_date = "%s-03-31 23:59:59" % year
                else:
                    start_date = "%s-04-01 00:00:00" % year
            elif now.strftime('%m') in q3:
                if now.strftime('%m') == '07':
                    start_date = "%s-04-01 00:00:00" % year
                    end_date = "%s-06-30 23:59:59" % year
                else:
                    start_date = "%s-07-01 00:00:00" % year
            else:
                if now.strftime('%m') == '10':
                    start_date = "%s-07-01 00:00:00" % year
                    end_date = "%s-09-30 23:59:59" % year
                else:
                    start_date = "%s-10-01 00:00:00" % year
        elif self.type == 'year':
            #计算本年度的销售量，如果本月是本年的第一个月，则计算上一个年度
            if now.strftime('%m') == '01':
                pre_year = str(int(year) - 1)
                start_date = "%s-01-01 00:00:00" % pre_year
                end_date = "%s-12-31 23:59:59" % pre_year
            else:
                end_date = now.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
                start_date = "%s-01-01 00:00:00" % year
        else:
            #自定义时间段
            if self.start_date and self.end_date:
                if self.end_date < self.start_date:
                    raise exceptions.UserError(u'开始时间不能大于结束时间')
                start_date = self.start_date + ' 00:00:00'
                end_date = self.end_date + ' 23:59:59'
            else:
                raise exceptions.UserError(u'起止时间必须填写')
        lines = self.get_lines(start_date, end_date)
        self.write({'line_ids': lines})
        return self.re_open()
    @api.multi
    def re_open(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'context': self._context,
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('product_manage_x.product_manage_wizard_form').id,
            'target': 'new',
        }

    @api.multi
    def confirm(self):
        self.ensure_one()
        order = self.env['product.manage'].browse(self._context.get('active_ids'))[0]
        product_lines = []
        for line in self.line_ids:
            vals = {
                'product_id': line.product_id.id,
                'percent': line.product_percent,
                'qty': line.qty,
            }
            product_lines.append((0,0,vals))
        order.write({'line_ids': product_lines})
        return True

class ProductLines(models.TransientModel):
    _name = 'product.manage.wizard.line'

    product_id = fields.Many2one('product.product', string='Product')
    order_id = fields.Many2one('product.manage.wizard', string='Order')
    uom_id = fields.Many2one(related='product_id.uom_id', string='Uom')
    qty = fields.Float(string='Qty')
    product_percent = fields.Float(string='Per Percent')
