# -*- coding: utf-8 -*-
{
    'name': "company_counter",

    'summary': """
        柜台管理""",

    'description': """
        Long description of module's purpose
    """,

    'author': "cloudy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/company_counter.xml',
        'views/base_template.xml',
        'views/counter_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}