# -*- coding: utf-8 -*-
{
    'name': "库存导入修改",

    'summary': """
        库存盘点时，从excel中导入库存数据""",

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
    'depends': ['base','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/stock_import.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
      
    ],
}