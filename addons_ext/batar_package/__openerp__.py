# -*- coding: utf-8 -*-
{
    'name': "Batar 产品包装",
    'author': 'Xiao',
    'category': 'Batar',
    'summary': 'package info',
    'depends': ['base', 'product'],
    'data': ['wizard/split_package_wizard.xml',
             'data/batar_package_data.xml',
            'security/ir.model.access.csv',
             ],
    'description': """
    包装信息
    """,
    'application': True,
}