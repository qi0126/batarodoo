# -*- coding: utf-8 -*-
{
    'name': "Product Manage",
    'author': 'Xiao',
    'category': 'Batar',
    'summary': 'product active',
    'depends': ['product', 'product_menu'],
    'data': [
        'security/product_manage_security.xml',
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/product_manage_wizard_view.xml',
        'data/product_manage_data.xml',
    ],
    'description': """
    根据产品销售量，上下架产品。
    """,
    'application': True,
}