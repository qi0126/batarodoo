# -*- coding: utf-8 -*-
{
    'name': "产品信息扩展",

    'summary': """
        增加单品优惠工费和单品 折扣""",

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
    'depends': ['base','product','product_menu', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
#         'views/product_supplier.xml',
        'views/multi_product_attribute.xml',
        'data/product_attribute_init.xml',
        'views/product_product.xml',
        'views/product_template.xml',
        'views/product_attribute.xml',
        'views/product_attribute_price.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
}