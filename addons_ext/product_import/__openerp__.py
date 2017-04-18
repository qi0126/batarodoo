# -*- coding: utf-8 -*-
{
    'name': "产品导入",

    'summary': """
        从excel中产品导入""",

    'description': """
                商品 导入 
    """,

    'author': "cloudy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','purchase','product_menu'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
#         'product_category_data.xml',
        'wizard/product_import.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
    
    ],
}