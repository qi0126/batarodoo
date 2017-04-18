# -*- coding: utf-8 -*-
{
    'name': "Batar 克重",
    'author': 'Xiao',
    'category': 'Batar',
    'summary': 'weight manage',
    'depends': ['product', 'stock', 'batar_stock_menu'],
    'data': ['views/batar_weight_view.xml'],
    'description': """
    称重时，记录实际净重跟标准净重的误差，入库或盘点时：实际净重-标准净重，出库时：标准克重-实际净重
    """,
    'application': True,
}