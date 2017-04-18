# -*- coding: utf-8 -*-
{
    'name': "batar_purchase_apply_order",

    'summary': """
        申购单""",

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
    'depends': ['base','product','purchase','batar_product_supplier'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',

        'views/purchase_apply_order.xml',
        'views/purchase_apply_order_line.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}