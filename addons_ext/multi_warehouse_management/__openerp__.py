# -*- coding: utf-8 -*-
{
    'name': "多仓库管理",

    'summary': """
        多仓库管理，仓管人员只能看到自己的仓库""",

    'description': """
        多仓库管理，仓管人员只能看到自己的仓库
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
        'views/multi_warehose_management.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
}