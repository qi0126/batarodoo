# -*- coding: utf-8 -*-
{
    'name': 'Batar payment',
    'author': 'Xiao',
    'description': """
    AU payment
    """,
    'depends': ['base', 'account', 'product', 'sale'],
    'data': [
        'views/batar_lailiao_view.xml',
        'views/partner_view.xml',
        'views/product_view.xml',
        'views/sale_view.xml',
    ],
    'application': True,

}