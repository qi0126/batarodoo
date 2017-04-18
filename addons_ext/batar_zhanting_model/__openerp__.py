# -*- coding: utf-8 -*-
{
    'name': "batar_zhanting_model",

    'summary': """
        展厅模块需要依赖的字段""",

    'description': """
        Long description of module's purpose
    """,

    'author': "cloudy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','stock','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/product_category.xml',
        'views/sale_order.xml',
        'views/res_user.xml',
        'views/clean_yestoday_customer.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}