# -*- coding: utf-8 -*-
{
    'name': "batar_quality",

    'summary': """
        收货质量检测""",

    'description': """
        收货质量检测
    """,

    'author': "cloudy",
    'website': "http://www.batar.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock','batar_delivery_bill'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/quality_order.xml',
        'views/batar_delivery_bill.xml',
        'data/quality_reason.xml',
        'views/stock_pick_in.xml',
        'views/quality_back_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}