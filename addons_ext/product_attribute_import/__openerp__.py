# -*- coding: utf-8 -*-
{
    'name': "product_attribute_import",

    'summary': """
         产品属性导入""",

    'description': """
        产品属性导入
    """,

    'author': "cloudy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product_menu','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        "wizard/product_attribute_value_import.xml",
       
    ],
    # only loaded in demonstration mode
    'demo': [
      
    ],
}