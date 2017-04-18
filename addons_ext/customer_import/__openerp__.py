# -*- coding: utf-8 -*-
{
    'name': "客户信息导入",

    'summary': """
        从excel中导入客户信息""",

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
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        
        'wizard/customer_import.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}