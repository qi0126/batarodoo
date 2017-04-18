# -*- coding: utf-8 -*-
{
    'name': "Batar 内部调拨",
    'author': 'Xiao',
    'category': 'Batar',
    'summary': '',
    'depends': ['stock', 'batar_stock_menu'],
    'data': [
        'security/internal_trans_security.xml',
        'security/ir.model.access.csv',
        'views/sample_trans.xml',
        'data/sample_trans_data.xml',
        'views/internal_trans_wizard_view.xml',
        'views/template.xml',
    ],
    'description': """
    目前包含样品调拨
    """,
    'application': True,
}