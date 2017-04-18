# -*- coding:utf-8 -*-
{
    'name': u'Batar 盘点调库',
    'author': 'Xiao',
    'description': """
    库存盘点前的库位调整，调配多余托盘
    """,
    'depends': ['stock', 'batar_stock'],
    'data': [
        'views/batar_adjustment_view.xml',
        'security/ir.model.access.csv'
    ],
    'application': True
}