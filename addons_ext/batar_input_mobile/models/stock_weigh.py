# -*- coding: utf-8 -*-
from openerp import api, fields, models, exceptions
import re

class StockWeigh(models.Model):
    _inherit = 'stock.weigh'

    def _offset_weight_create(self, quality_line):
        # 如果有辅助单位，则生成重量差异单。
        weight_obj = self.env['batar.weight']
        if quality_line.product_id.support_uom:
            attribute_value_ids = quality_line.product_id.attribute_value_ids
            standard_weight = 0.0
            for a in attribute_value_ids:
                if a.attribute_id.code == "weight":
                    m = re.match(r"(^[0-9]\d*\.\d|\d+)", a.name)
                    weight = m.group(1)
                    standard_weight = float(weight)
                    break
            offset_weight = quality_line.actual_net_weight - standard_weight * quality_line.actual_product_qty
            ref = 'M-INPUT:' + quality_line.order_id.name
            weight_obj.create(
                {'product_id': quality_line.product_id.id, 'qty': quality_line.actual_product_qty,
                 'offset_weight': offset_weight, 'net_weight': quality_line.net_weight,'ref': ref})

    @api.model
    def change_plate(self):
        """
        质检换盘时，生成分拣任务
        """
        plate = self.env['quality.plate'].search([('state', '=', 'draft'), ('user_id', '=', self._context['uid'])])
        #克重差异记录模块
        if plate and plate.line_ids:
            input_obj = self.env['batar.input.mobile']
            input_lines = []
            # partner = plate.line_ids[0].quality_id.partner_id
            for line in plate.line_ids:
                vals = {
                    'product_id': line.product_id.id,
                    'sequence': line.sequence,
                    'qty': line.actual_product_qty,
                    'src_location': str(line.sequence),
                    'package': line.name,
                    'net_weight': line.actual_net_weight,
                    'gross_weight': line.actual_gross_weight,
                }
                input_lines.append((0,0,vals))
                #如果有辅助单位，则生成重量差异单。
                self._offset_weight_create(line)
            input_vals = {
                'user_id': plate.user_id.id,
                # 'partner_id': partner.id,
                'plate_id': plate.id,
                'line_ids': input_lines,
            }
            input_obj.create(input_vals)
        res = super(StockWeigh, self).change_plate()
        return res
    @api.model
    def split_plate_done(self):
        # res = super(StockWeigh, self).split_plate_done()
        plate = self.env['quality.plate'].search([('state', '=', 'draft'), ('user_id', '=', self._context['uid'])])
        if plate and plate.line_ids:
            input_obj = self.env['batar.input.mobile']
            input_lines = []
            for line in plate.line_ids:
                vals = {
                    'product_id': line.product_id.id,
                    'sequence': line.sequence,
                    'qty': line.actual_product_qty,
                    'src_location': str(line.sequence),
                    'package': line.name,
                    'net_weight': line.actual_net_weight,
                    'gross_weight': line.actual_gross_weight,
                }
                input_lines.append((0, 0, vals))
                # 如果有辅助单位，则生成重量差异单。
                self._offset_weight_create(line)
            input_vals = {
                'user_id': plate.user_id.id,
                'plate_id': plate.id,
                'line_ids': input_lines,
            }
            input_obj.create(input_vals)
            plate.state = 'wait_pick_in'
        else:
            raise exceptions.ValidationError(u"无未完成的盘")
    # @api.model
    # def check_done(self):
    #     plate = self.env['quality.plate'].search([('state', '=', 'draft'), ('user_id', '=', self._context['uid'])])
    #     if plate and plate.line_ids:
    #         input_obj = self.env['batar.input.mobile']
    #         input_lines = []
    #         # partner = plate.line_ids[0].quality_id.partner_id
    #         for line in plate.line_ids:
    #             vals = {
    #                 'product_id': line.product_id.id,
    #                 'sequence': line.sequence,
    #                 'qty': line.actual_product_qty,
    #                 'src_location': str(line.sequence),
    #                 'package': line.name,
    #                 'net_weight': line.actual_net_weight,
    #                 'gross_weight': line.actual_gross_weight,
    #             }
    #             input_lines.append((0,0,vals))
    #             # 如果有辅助单位，则生成重量差异单。
    #             self._offset_weight_create(line)
    #         input_vals = {
    #             'user_id': plate.user_id.id,
    #             # 'partner_id': partner.id,
    #             'plate_id': plate.id,
    #             'line_ids': input_lines,
    #         }
    #         input_obj.create(input_vals)
    #     res = super(StockWeigh, self).check_done()
    #     return res

    def _get_available_locations(self):
        #获取可用的库位推荐给分拣员
        location_obj = self.env['stock.location']
        location_domain = [('is_sample', '=', False), ('usage', '=', 'internal'), ('barcode', 'like', '-')]
        locations = location_obj.search(location_domain)
        quants = self.env['stock.quant'].search([])
        inuse_locations = quants.filter(lambda x: '-' in x.location_id.name).mapped('location_id')
        available_locations = locations - inuse_locations
        return available_locations