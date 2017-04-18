# -*- coding: utf-8 -*-
{
    'name': "销售订单改进",

    'summary': """
                改进销售订单增加新的字段，用于适合黄金等贵重物品销售的场景""",

    'description': """
        Long description of module's purpose
    """,

    'author': "cloudy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale','sale_stock','product_info_extend'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        
    ],
    'installable': True,
    
}