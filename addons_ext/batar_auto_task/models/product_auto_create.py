# -*- coding: utf-8 -*-
'''
Created on 2016年6月14日

@author: cloudy
'''
from openerp import models,api



class product_auto_create(models.TransientModel):
    _name = 'product.auto.create'
    
    @api.model
    def auto_create_product_variants(self):
        template_list = self.env['product.template'].search([('variants_create_auto','=','auto_create')])
        for tmpl_id in template_list:
            if tmpl_id.create_variant_ids():
                tmpl_id.variants_create_auto = 'yes'