# -*- coding:utf-8 -*-

from openerp import api, fields, models, _, exceptions
from lxml import etree


class ProductCategory(models.Model):
    _inherit = 'product.category'

    no_create_variants = fields.Boolean(
        string="Don't create variants automatically",
        help='This check disables the automatic creation of product variants '
             'for all the products of this category.', default=True)

    @api.multi
    @api.onchange('no_create_variants')
    def onchange_no_create_variants(self):
        self.ensure_one()
        if not self._origin:
            return {}
        return {'warning': {'title': u'警告!',
                            'message': u'修改此项将关联产品的自动创建',
                            }}

    @api.multi
    def write(self, values):
        res = super(ProductCategory, self).write(values)
        if ('no_create_variants' in values and
                not values.get('no_create_variants')):
            self.env['product.template'].search(
                [('categ_id', '=', self.id),
                 ('variants_create_auto', '=', 'category')]).create_variant_ids()
        return res


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    variants_create_auto = fields.Selection(
        [('yes', 'Create Auto'),
         ('no', "Don't create Auto"),
         ('category', 'use the category value'),
         ('auto_create','background auto create')
         ], required=True, string="Create Auto", default='no')

    @api.multi
    @api.onchange('variants_create_auto')
    def onchange_no_create_variants(self):
        self.ensure_one()
        if not self._origin:
            return {}
        return {'warning': {'title': u'警告!',
                            'message': u'修改此项将关联产品的自动创建',
                            }}

    @api.multi
    def write(self, values):
        res = super(ProductTemplate, self).write(values)
        if 'variants_create_auto' in values:
            self.create_variant_ids()
        return res
    @api.multi
    def create_variant_ids(self):
        for tmpl in self:
            if ((tmpl.variants_create_auto == 'category' and
                    not tmpl.categ_id.no_create_variants) or
                    (tmpl.variants_create_auto == 'yes')):
                return super(ProductTemplate, self).create_variant_ids()
            else:
                return True

class Product(models.Model):

    _inherit = 'product.product'


    @api.onchange('product_tmpl_id')
    def product_tmpl_values_onchange(self):
        if self.product_tmpl_id:
            values = self.env['product.attribute.value']

            attribute_line = self.env['product.attribute.line'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)])
            attribute_line = self.env['product.attribute.line'].search(
                [('product_tmpl_id', '=', self.product_tmpl_id.id)])
            for i in attribute_line:
                values += i.value_ids
            return {'domain': {'attribute_value_ids': [('id', 'in', values.ids)]}}
        else:
            return {'domain': {'attribute_value_ids': [('id', 'in', [])]}}

            # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(Product, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     doc = etree.XML(res['arch'])
    #     domain = []
    #     if self._context.get('product_tmpl_id'):
    #         values = self.env['product.attribute.value']
    #         attribute_line = self.env['product.attribute.line'].search([('product_tmpl_id', '=', self._context['product_tmpl_id'])])
    #         for i in attribute_line:
    #             values += i.value_ids
    #         domain = [('id', 'in', values.ids)]
    #         for node in doc.xpath("//field[@name='attribute_value_ids']"):
    #             node.set('domain', str(domain))
    #         res['arch'] = etree.tostring(doc)
    #
    #     return res
    # # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(Product, self).fields_view_get(
    #         view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if self._context.get('type'):
    #         if self.product_tmpl_id:
    #             value_ids = []
    #             values = None
    #             domain = []
    #             attribute_line = self.env['product.attribute.line'].search(
    #                 [('product_tmpl_id', '=', self.product_tmpl_id.id)])
    #             for i in attribute_line:
    #                 values += i.value_ids
    #             if values:
    #                 str = ",".join(values.ids)
    #                 str = "[%s]" % str
    #                 domain = "[('attribute_value_ids','in',%s)]" % str
    #             doc = etree.XML(res['arch'])
    #             for node in doc.xpath("//field[@name='attribute_value_ids']"):
    #                 node.set('domain', domain)
    #             res['arch'] = etree.tostring(doc)
    #     return res


