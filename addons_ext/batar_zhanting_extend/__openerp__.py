# -*- coding: utf-8 -*-
{
    'name': "batar_zhanting_extend",

    'summary': """
        展厅下单模块升级版""",

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
    'depends': ['base','batar_zhanting_model','customer_extend','sale_order_extend', 'batar_sale_state','batar_zhanting_order','batar_stock_pick_add'],

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