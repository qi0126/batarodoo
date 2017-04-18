# -*- coding: utf-8 -*-
{
    'name': "Sample Location code",
    'author': 'Xiao',
    'category': 'Batar',
    'summary': '',
    'depends': ['stock', 'product', 'batar_stock_menu', 'batar_zhanting_extend', 'internal_trans_mobile'],
    'data': ['views/sample_location_code_view.xml',
             'security/ir.model.access.csv',
             ],
    'description': """
    为产品添加柜台货号
    """,
    'application': True,
}