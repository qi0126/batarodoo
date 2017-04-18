# -*- coding: utf-8 -*-
{
    'name': u'Batar 手机分拣助手',
    'author': 'Xiao',
    'depends': ['batar_stock', 'batar_zhanting_extend', 'batar_sale_state', 'batar_stock_menu'],
    'data': [
        'security/batar_mobile_picking_security.xml',
        'security/ir.model.access.csv',
        'views/batar_mobile_picking.xml',
        'views/stock_pick_view.xml',
        'data/mobile_pick_sequence.xml',
    ],
    'application': True,
}