# -*- coding: utf-8 -*-
{
    'name': " 出库质检",

    'summary': """
        客户出库质检操作""",

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
    'depends': ['base','stock','batar_package','mobile_picking_v2','out_quality_order','batar_stock_pick_add'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'qweb': ['static/src/xml/*.xml'],
}