# -*- coding: utf-8 -*-

from openerp import fields,models

class res_country_state_city(models.Model):
    _name = 'res.country.state.city'
   
    name = fields.Char(size=50,string='city name')
    province_id = fields.Many2one('res.country.state',ondelete='cascade',string='province name')
    district_ids = fields.One2many('res.country.state.city.district','city_id',string='districts belong to one city')
    country_id = fields.Many2one(related='province_id.country_id',string='country')
    
 
class res_country_state_city_district(models.Model):
    _name = 'res.country.state.city.district'
    
    name = fields.Char(size=100,string='district name')
    city_id = fields.Many2one('res.country.state.city',ondelete='cascade',string='city name')
    province_id = fields.Many2one(related='city_id.province_id',string='province')
    country_id = fields.Many2one(related='province_id.country_id',string='country')
        
    
 
class res_country_state(models.Model):
    _inherit = 'res.country.state'
    
    city_ids= fields.One2many('res.country.state.city','province_id',string='citys belong to one state')
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: