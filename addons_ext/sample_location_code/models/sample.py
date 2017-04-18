# -*- coding: utf-8 -*-
from openerp import api, fields, models, exceptions
import openerp.addons.decimal_precision as dp

class Code(models.Model):
    _name = 'sample.location.code'

    name = fields.Integer(string='Code')
    product_id = fields.Many2one('product.product', string='Product')
    location_id = fields.Many2one('stock.location', string='Location')
    active = fields.Boolean(string='Active', default=True)
    net_weight = fields.Float(string='Net Weight')

    _sql_constraints = [
        # ('name_uniq', 'unique(name,location_id,active)', u"柜台内货号必须唯一"),
        ('check_name', 'CHECK (name<10000)', u'柜台内货号必须小于10000'),
    ]
    @api.multi
    def _check_name(self):
        if len(self.ids) == len(self.mapped('name')):
            return True
        else:
            return False
    _constraints = [(_check_name, u"柜台内货号必须唯一", ['name'])]

class StockLocation(models.Model):
    _inherit = 'stock.location'

    code_ids = fields.One2many('sample.location.code', 'location_id', string='Code')
    code_counts = fields.Integer(string='Counts of Code', compute='_compute_code_counts')

    @api.multi
    @api.depends('code_ids')
    def _compute_code_counts(self):
        for line in self:
            line.code_counts = len(line.code_ids)

    @api.multi
    def action_code_view(self):
        self.ensure_one()
        action = self.env.ref('sample_location_code.action_sample_location_code')
        result = {
            'name': action.name,
            'type': action.type,
            'view_mode': action.view_mode,
            'view_type': action.view_type,
            'target': action.target,
            'context': "{'search_default_location_id': active_id}",
            'res_model': action.res_model,
        }
        code_ids = self.code_ids.ids
        result['domain'] = [('id', 'in', code_ids)]
        return result

class TransLine(models.Model):
    _inherit = 'trans.mobile.lines'

    code = fields.Integer(string='Location Code', readonly=True)
    product_id = fields.Many2one(readonly=True)
    qty = fields.Float(readonly=True)
    src_location = fields.Many2one(readonly=True)
    dest_location = fields.Many2one(readonly=True)
    net_weight = fields.Float(readonly=True)
    gross_weight = fields.Float(readonly=True)
    sequence = fields.Integer(readonly=True)
    panwei = fields.Char(readonly=True)
    state = fields.Selection(readonly=True)
    uom_id = fields.Many2one(readonly=True)
class SampleMobile(models.Model):
    _inherit = 'internal.trans.mobile'

    line_ids = fields.One2many(states={'tag': [('readonly', False)]})
    @api.multi
    def confirm_tag(self):
        #标签完之后，完成入样品库
        self.ensure_one()
        if self.state == 'tag':
            if any([a.code > 0 for a in self.line_ids]):
                for line in self.line_ids.filtered(lambda x: x.code != None):
                    code_obj = self.env['sample.location.code']
                    if code_obj.search([('name', '=', line.code), ('location_id', '=', self.trans_id.location_id.id)]):
                        location = self.trans_id.location_id
                        name = location.name
                        while location.location_id and location.usage != 'view':
                            location = location.location_id
                            name = location.name + '/' + name
                        raise exceptions.UserError(u"货号: %s,在 %s 中已使用！" % (line.code, name))
                    vals = {
                        'product_id': line.product_id.id,
                        'location_id': self.trans_id.location_id.id,
                        'name': line.code,
                        'net_weight': line.net_weight,
                    }
                    self.env['sample.location.code'].create(vals)
            self.write({'state': 'done'})
            self.trans_id.picking_ids.do_new_transfer()
            self.trans_id.write({'state': 'done'})
        return self.line_ids.print_product_tag()
    @api.model
    def confirm_task(self, line_id):
        #手机端确认完成任务
        line = self.env['trans.mobile.lines'].browse([line_id])
        request_order = line.order_id.trans_id
        line.order_id.write({'state': 'done'})
        picks = request_order.picking_ids
        try:
            picks.action_confirm()
            picks.action_assign()
            picks.do_new_transfer()
            return True
        except:
            print 'False'
            return False
    @api.model
    def get_out_plate(self, task_id):
        #质检员处领取物品
        task = self.browse([task_id])
        # task.write({'state': 'process'})
        line = task.line_ids[0]
        line.write({'state': 'process'})
        data = self.get_line_value(line)
        return {'code': '201', 'data': data}
    @api.model
    def get_out_next(self, line_id, location):
        #样品调拨存储库，由于没有先生成内部调拨单，所以下一条的处理异于之前的操作
        #由申请单审批后，生成质检单后，进行分盘，排序，按顺序分拣
        line = self.env['trans.mobile.lines'].browse([line_id])
        des_location = self.env['stock.location'].search([('barcode', '=', location)])
        picking_type_id = self.env['stock.picking.type'].with_context(lang='en').search(
            [('name', 'ilike', 'Internal Transfers')], limit=1)
        picking_obj = self.env['stock.picking']
        if line:
            if des_location:
                #分拣行写入目标库位，并标记为完成
                line.write({'state': 'done', 'dest_location': des_location.id})
                if all([a.state == 'done' for a in line.order_id.line_ids]):
                    #如果全部明细已经完成，则返回 400，当前分拣明细,并生成对应的内部调拨单
                    data = self.get_line_value(line)
                    total = sum([x.qty for x in line.order_id.line_ids])
                    data['total'] = total
                    #内部调拨单中加入move 明细，并确认
                    location_dest = []
                    internal_pick = self.env['stock.picking']
                    for trans_line in line.order_id.line_ids:
                        move_vals = {
                            'product_id': trans_line.product_id.id,
                            'location_id': line.order_id.location_id.id,
                            'location_dest_id': des_location.id,
                            'product_uom': trans_line.product_id.uom_id.id,
                            'product_uom_qty': trans_line.qty,
                            'name': 'OUT:samplemove',
                            'origin': 'SAMPLE:' + line.order_id.name
                        }
                        if trans_line.dest_location.id not in location_dest:
                            location_dest.append(des_location.id)
                            # 根据明细生成内部调拨单
                            vals = {
                                # 'location_id': picking_type_id.default_location_src_id.id,
                                # 'location_dest_id': self.location_id.id,
                                'location_id': line.order_id.location_id.id,
                                'location_dest_id': des_location.id,
                                'picking_type_id': picking_type_id.id,
                                'sample_trans_id': line.order_id.trans_id.id,
                                'move_lines': [(0, 0, move_vals)]
                            }
                            internal_pick += picking_obj.create(vals)
                        else:
                            internal_pick.filtered(lambda x: x.location_dest_id == trans_line.dest_location).write({'move_lines_related': [(0, 0, move_vals)]})
                    # try:
                    #     internal_pick.action_confirm()
                    #     internal_pick.action_assign()
                    #     internal_pick.do_new_transfer()
                    # except:
                    #     print 'False'
                    #     return False
                    code_obj = self.env['sample.location.code']
                    domain = [('name', 'in', line.order_id.line_ids.mapped('code')), ('location_id', '=', line.order_id.location_id.id)]
                    codes = code_obj.search(domain)
                    if codes:
                        codes.write({'active': False})
                    # line.order_id.write({'state': 'done'})
                    return {'code': '400', 'data': data}
                else:
                    #如果未全部完成，则返回未草稿的第一条任务
                    next_line = line.order_id.mapped('line_ids').filtered(lambda x: x.state == 'draft')
                    next_line.write({'state': 'process'})
                    data = self.get_line_value(next_line[0])
                    return {'code': '201', 'data': data}
            else:
                #输入的目标库位不存在 code: 501
                return {'code': '501', 'data': {}}
        else:
            #输入的产品货号有误 code 502
            return {'code': '500', 'data': {}}
    @api.model
    def comfirm_out(self, task_id):
        #完成调出任务，任务标记完成，并根据明细生成原始内部调拨单据
        task = self.browse([task_id])
        task.write({'state': 'done'})
        locations = task.line_ids.mapped('des_location')
        for location in locations:
            vals = {
                'mobile_user': task.user_id,
                'location_id': task.location_id.id,
                'des_location': location.id,
            }
class WizardLine(models.TransientModel):
    _inherit = 'sample.trans.line'

    code = fields.Integer(string='Location Code', readonly=True)
    net_weight = fields.Float(string='Net Weight', digits=dp.get_precision('Batar price'))
class TransWizard(models.TransientModel):
    _inherit = 'sample.trans.wizard'
    @api.onchange('product_code')
    def onchange_sample_line(self):
        product_obj = self.env['product.product']
        quant_obj = self.env['stock.quant']
        order = self.env['batar.sample.trans'].browse(self._context.get('active_ids'))[0]
        line_ids = []
        inuse_location = []
        sample_location = order.location_id
        for line in self.line_ids:
            line_ids.append((4, line.id, 0))
            inuse_location.append(line.src_location.id)
        if self.product_code:
            if order.type == 'out':
            #样品调出，扫码后，先尝试转码为数字，优先货号查找，再查找内部编号
                try:
                    code = int(self.product_code)
                    search_list = [('active', '=', True), ('location_id', '=', sample_location.id), ('name', '=', code)]
                    sample_code = self.env['sample.location.code'].search(search_list)
                except:
                    raise exceptions.UserError(u'货号不存在，或格式错误，请输入正确的货号')
                vals = {
                    'product_id': sample_code.product_id.id,
                    'qty': 1,
                    'src_location': sample_location.id,
                    'code': sample_code.name,
                    'net_weight': sample_code.net_weight,
                }
                line_ids.append((0, 0, vals))
                self.line_ids = line_ids
            else:
                res = super(TransWizard, self).onchange_sample_line()
                return res
    @api.multi
    def confirm(self):
        self.ensure_one()
        order = self.env['batar.sample.trans'].browse(self._context.get('active_ids'))[0]
        trans_lines = []
        for line in self.line_ids:
            vals = {
                'product_id': line.product_id.id,
                'src_location': line.src_location.id,
                'dest_location': order.location_id.id,
                'qty': line.qty,
                'code': line.code,
                'net_weight': line.net_weight,
            }
            trans_lines.append((0,0,vals))
        order.write({'line_ids': trans_lines})
        return True

class Lines(models.Model):
    _inherit = 'sample.trans.lines'

    code = fields.Integer(string='Location Code', readonly=True)
    net_weight = fields.Float(string='Net Weight', digits=dp.get_precision('Batar price'))
class SampleTrans(models.Model):
    _inherit = 'batar.sample.trans'

    @api.multi
    def action_part_confirm(self):
        #新增自动分配货号
        res = super(SampleTrans, self).action_part_confirm()
        trans_obj = self.env['internal.trans.mobile']
        loc_obj = self.env['sample.location.code']
        trans_order = trans_obj.search([('trans_id', '=', self.id)])
        undone_trans = trans_obj.search([('state', '!=', 'done'), ('location_id', '=', self.location_id.id)])
        undone_trans_lines = []
        #当前样品库调入的未完成订单明细中已分配的货号
        if undone_trans:
            undone_trans_lines = [ line.code for trans in undone_trans for line in trans.line_ids if line.code != 0]
        loc_orders = loc_obj.search([('location_id', '=', self.location_id.id)])
        if loc_orders or undone_trans_lines:
            # range当前最大货号 - （当前样品库中已分配货号 + 未完成订单分配货号）= 已释放的可用货号
            inuse_code = loc_orders.mapped('name') + undone_trans_lines
            avaliable_code = list(set([a for a in range(1, max(inuse_code)+1)]) - set(inuse_code))
            code = max(inuse_code) + 1
            for line in trans_order.line_ids:
                if len(avaliable_code) > 0:
                    line.code = avaliable_code.pop(0)
                else:
                    #已释放货号全部使用后，继续当前最大货号之后增加
                    if code < 10000:
                        line.code = code
                        code += 1
        else:
        #从未分配货号
            code = 1
            for line in trans_order.line_ids:
                if code < 10000:
                    line.code = code
                    code += 1
        return  res