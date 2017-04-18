# -*- coding: utf-8 -*-
{
    'name': "Batar 调拨助手",
    'author': 'Xiao',
    'category': 'Batar',
    'summary': '',
    'depends': ['batar_internal_trans', 'batar_stock_menu', 'batar_mobile_task'],
    'data': [
        'security/ir.model.access.csv',
        'views/trans_mobile_view.xml',
        'data/trans_mobile_data.xml',
        'views/line_product_tag.xml',
        'report/report_line_product_tag.xml',
    ],
    'description': """
    内部调拨生成分拣任务，目前包含样品调拨生成分拣任务。
    """,
    'application': True,
}