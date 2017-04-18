# -*- coding: utf-8 -*-
from odoo import http

# class CompanyCounter(http.Controller):
#     @http.route('/company_counter/company_counter/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/company_counter/company_counter/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('company_counter.listing', {
#             'root': '/company_counter/company_counter',
#             'objects': http.request.env['company_counter.company_counter'].search([]),
#         })

#     @http.route('/company_counter/company_counter/objects/<model("company_counter.company_counter"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('company_counter.object', {
#             'object': obj
#         })