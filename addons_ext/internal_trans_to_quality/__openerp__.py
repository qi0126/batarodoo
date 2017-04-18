# -*- coding: utf-8 -*-
{
    'name': "internal_trans_to_quality",

    'summary': """
        内部调拨生成质检单""",

    'description': """
        Long description of module's purpose
    """,

    'author': "",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','batar_internal_trans','batar_quality','sample_location_code'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}