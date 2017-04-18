# -*- coding: utf-8 -*-
{
    'name': u'Batar 订单状态管理',
    'author': 'Xiao',
    'depends': ['batar_stock_return','sale'],
    'data': [
        'views/batar_sale_state.xml',
    ],
    'description': """
    根据PICKING单据在不同分拣类型中的阶段来管理对应销售订单的状态。
    """,
    'application': True,
}