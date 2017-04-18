# -*- coding: utf-8 -*-
'''
Created on 2016年3月11日

@author: cloudy
'''

from openerp import fields,models,api

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    district_id = fields.Many2one('res.country.state.city.district',store=True,string='district')
    city_id = fields.Many2one(related='district_id.city_id',store=True,string='city')
    province_id = fields.Many2one(related='city_id.province_id',store=True,string='province')
    country_id = fields.Many2one(related='province_id.country_id', store=True,string='country')
    

    
    
