# -*- coding: utf-8 -*-
{
    'name': "batar_delivery_receive",

    'summary': """
        收货，在送货单导入系统后，接收供应商的货物，可根据送货单收货，也可根据包号收货""",

    'description': """
        Long description of module's purpose
    """,

    'author': "cloudy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','batar_delivery_bill','batar_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/batar_delivery_receive.xml',
        'views/stock_picking.xml',
       
    ],
    # only loaded in demonstration mode
    'demo': [
    
    ],
}