# -*- coding: utf-8 -*-
{
    'name': "batar_stock_weigh",

    'summary': """
        称重界面""",

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
    'depends': ['base','web','batar_quality','product_info_extend','batar_package'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'qweb': ['static/src/xml/*.xml'],
}