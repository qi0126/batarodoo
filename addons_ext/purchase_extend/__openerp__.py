# -*- coding: utf-8 -*-
{
    'name': "purchase_extend",

    'summary': """
        采购单改进""",

    'description': """
        采购单改进，限制客户只能为公司
    """,

    'author': "cloudy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_template.xml',
       'views/purchase_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
      
    ],
}