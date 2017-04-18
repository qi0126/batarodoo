# -*- coding: utf-8 -*-
{
    'name': "库存改进",

    'summary': """
        根据需要改进库存管理功能""",

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
    'depends': ['base','stock','product_info_extend','procurement_order'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/stock_move.xml',
        'views/stock_pack_operation.xml',
        'views/stock_picking.xml',
#         'views/stock_product_detail.xml',
       
       
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}