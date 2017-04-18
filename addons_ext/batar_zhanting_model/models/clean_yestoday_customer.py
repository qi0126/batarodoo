# -*- coding: utf-8 -*-
'''
Created on 2016年8月23日

@author: cloudy
'''
from openerp import models,api


class CleanCustomer(models.Model):
    _name='clean.customer'

    @api.model
    def clean_customer(self):
        '''清理当天的客户信息'''
        users = self.env['res.users'].search([('active','=',True)])
        for user in users:
            user.current_customer = None
        recent_customers = self.env['recent.customer'].search([('user_id','in',[line.id for line in users])])
        for line in recent_customers:
            line.unlink()

