# -*- coding: utf-8 -*-
{
    'name': "batar_auto_task",

    'summary': """
       后台自动创建产品规格""",

    'description': """
        后台自动创建产品规格
    """,

    'author': "cloudy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','batar_product_no_autocreate','product_info_extend'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_auto_create.xml',
        'wizard/product_template.xml',
       
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,
}