# -*- coding: utf-8 -*-
{
    'name': "Batar 手机分拣助手V1.2",
    'author': 'Xiao',
    'category': 'Batar',
    'summary': 'update mobile picking',
    'depends': ['batar_mobile_picking', 'batar_package'],
    'data': ['views/mobile_picking_view.xml',
             'report/report_package_picking.xml',
             'views/report_template_package.xml',
             ],
    'description': """
    1115期手机分拣助手功能更新，包含打包过程（称重，贴标签）
    """,
    'application': True,
}