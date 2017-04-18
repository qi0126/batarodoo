# -*- coding: utf-8 -*-
{
    'name': u'Batar 客户单据',
    'author': 'Xiao',
    'description': """

    """,
    'depends': ['base','batar_zhanting_model','customer_extend','sale_order_extend', 'batar_sale_state'],
    'data': [
        'security/ir.model.access.csv',
        'views/batar_zhanting_order_view.xml',
        'views/customer_sale_task.xml',
    ],
    'application': True,
}