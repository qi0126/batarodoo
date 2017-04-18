# -*- coding: utf-8 -*-
{
    'name': "产品菜单",

    'summary': """
        将产品相关的提取作为单独的菜单""",

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
    'depends': ['base','product'],

    # always loaded
    'data': [
        'security/product_manage.xml',
#         'security/ir.model.access.csv',
        'views/product_menu.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
}