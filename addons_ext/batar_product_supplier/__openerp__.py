# -*- coding: utf-8 -*-
{
    'name': "batar_product_supplier",

    'summary': """
       产品供应商""",

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
    'depends': ['base','product', 'product_menu'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_supplier_import.xml',
        'views/product_product.xml',
        'views/product_supplier.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}