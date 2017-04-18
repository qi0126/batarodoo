#!/usr/bin/env python
# encoding: utf-8
"""
@project:odoo.btr
@author:cloudy
@site:
@file:batar_product_category.py
@date:2016/11/8 10:04
"""
from openerp import  models,fields,api,_


class batar_product_category(models.Model):
    """企业产品分裂"""
    _name = 'batar.product.category'

    name = fields.Char(string='batar category name')
    parent_id = fields.Many2one("batar.product.category",string='parent category name',ondelete='cascade')
    child_id = fields.One2many("batar.product.category",'parent_id',string='child category name')
    full_path = fields.Char(compute="_full_path_get", string='full path')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('category name must be unique!')),
    ]
    @api.one
    @api.depends("parent_id")
    def _full_path_get(self):
        """全路径名称"""
        full_list = [self.name]
        parent = self.parent_id
        while True:
            if parent:
                full_list.insert(0,parent.name)
                parent = parent.parent_id
            else:
                break
        self.full_path = '/'.join(full_list)

class product_template(models.Model):
    '''产品模版'''
    _inherit = 'product.template'

    batar_cate_id = fields.Many2one('batar.product.category',string='batar category name')