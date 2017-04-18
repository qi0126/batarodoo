# -*- coding: utf-8 -*-
{
    'name': "batar_product_template_import",

    'summary': """
        产品款式及款式属性信息导入""",

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
    'depends': ['base','product_menu','batar_product_category'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/product_template_import.xml',
        'wizard/product_template_attribute_import.xml',
        'views/product_template.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}