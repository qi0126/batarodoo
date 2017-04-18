# -*- coding: utf-8 -*-
{
    'name': "out_quality_order",

    'summary': """
        出库客户质检单据""",

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
    'depends': ['base','mobile_picking_v2','batar_stock_weigh'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/out_quality_order.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}