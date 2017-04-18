# -*- coding: utf-8 -*-
{
    'name': "batar_stock_pick_add",

    'summary': """
        仓库根据客户需求增加新的出库""",

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
    'depends': ['base','procurement','purchase','stock','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock_pick_add.xml',
        
        
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
}