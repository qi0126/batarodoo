# -*- coding: utf-8 -*-
{
    'name': "batar_sale_lock",

    'summary': """
        锁库""",

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
    'depends': ['base','sale_order_extend','batar_stock_pick_add','product_info_extend','batar_zhanting_order'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/view_sales_config.xml',
        'views/product_view.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}