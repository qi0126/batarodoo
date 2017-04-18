# -*- coding: utf-8 -*-
{
    'name': "procurement_order",

    'summary': """
        订单流程改进，增加响应的信息""",

    'description': """
        订单流程改进，增加响应的信息
    """,

    'author': "cloudy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','procurement','stock','sale_order_extend'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
}