# -*- coding: utf-8 -*-
{
    'name': "batar_product_category",

    'summary': """
        珠宝分类""",

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
    'depends': ['base','product','product_menu'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/batar_product_category_import.xml',
        'views/product_template.xml',
        'views/barar_product_category.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}