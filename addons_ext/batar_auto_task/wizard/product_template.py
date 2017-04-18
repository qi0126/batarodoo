# -*- coding: utf-8 -*-
'''
Created on 2016年6月16日

@author: cloudy
'''
from openerp import fields,models,api

class product_template_task(models.TransientModel):
    _name ='product.template.task'
    
    variants_create_auto = fields.Selection(
        [('yes', 'Create Auto'),
         ('no', "Don't create Auto"),
         ('category', 'use the category value'),
         ('auto_create','background auto create')
         ],string="Create Auto", default='no')
    
    @api.multi
    def apply(self):
        ''''''
        products = self.env['product.template'].browse(self._context.get('active_ids', []))
        vals = {}
        vals['variants_create_auto'] =self.variants_create_auto
        products.write(vals)