# -*- coding: utf-8 -*-
{
    'name': "product_label",

    'summary': """
        产品标签打印""",

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
    'depends': ['base','batar_delivery_bill','product_menu'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/delivery_bill_line_report_menu.xml',
        'report/report_delivery_bill_line.xml',
        'views/product_label.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
}