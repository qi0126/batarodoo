# -*- coding: utf-8 -*-
{
    'name': "Batar 手机分拣入库",
    'author': 'Xiao',
    'category': 'Batar',
    'summary': 'Input Task',
    'depends': ['base', 'product', 'stock',
                'batar_stock_weigh',
                'batar_weight',
                'batar_stock_menu',
                'batar_quality',
                ],
    'data': [
        'security/batar_input_mobile_security.xml',
        'security/ir.model.access.csv',
        'views/batar_input_mobile_view.xml',
        'data/batar_input_mobile_data.xml',
             ],
    'description': """
    手机分拣入库
    """,
    'application': True,
}