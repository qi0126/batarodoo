# -*- coding: utf-8 -*-
{
    'name': "customer_info_extend",

    'summary': """
        客户产品优惠信息，利息信息""",

    'description': """
               客户产品优惠信息，利息信息
    """,

    'author': "cloudy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','product_info_extend'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/customer_ornament_price.xml',
        'views/product_discount.xml',
        'views/res_partner.xml',
         
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}