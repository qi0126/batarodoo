# -*- coding: utf-8 -*-
'''
Created on 2016年2月25日

@author: cloudy
'''
from openerp import fields,models,api
from openerp.tools.common_ext import GetNextSequence
from openerp.exceptions import UserError,ValidationError

# import openerp.addons.decimal_precision as dp

class product_template(models.Model):
    _inherit = "product.template"
    
    ponderable = fields.Boolean(string='ponderable')
    sequence = fields.Integer(string='sequence',default=1)
    name= fields.Char('Name', required=True, translate=False, select=True)
    _defaults = {
        'type': "product",
        'ponderable':True,
        'categ_id':2,
       
    }
    # _sql_constraints = [
    #     ('name_uniq', 'unique(name)', 'product template name must be unique!'),
    # ]
   
   
    @api.model
    def create(self, vals):

        material_id = self.env['ir.model.data'].get_object_reference('product_info_extend', 'product_attribute_material')[1]
         
        templateObj = self.env['product.template'].search([],limit=1,order='id desc')
        sequence = 1
        if templateObj:
            sequence = GetNextSequence.GetNextSequence(templateObj.sequence)
        vals['sequence'] = sequence
        return super(product_template,self).create(vals)

