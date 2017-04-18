# -*- coding: utf-8 -*-
{
    'name': "batar_delivery_bill",

    'summary': """
        送货单""",

    'description': """
        Long description of module's purpose
    """,

    'author': "cloudy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'batar',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/delivery_bill_view.xml',
        'wizard/delivery_bill_import.xml',
        
        
         
    ],
    # only loaded in demonstration mode
    'demo': [
         
    ],
}