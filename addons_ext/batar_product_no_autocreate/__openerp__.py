# -*- coding: utf-8 -*-
{
    'name': 'Product no autocreate',
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    'category': 'batar',
    'description': """
    This module creates a check in categories and an option in product templates,
so that it does not create the product variants when the attributes are
assigned. This is used by those modules that create the product when it is
estrictly necessary
    """,
    'depends': ['base', 'product'],
    'data': ['views/product_view.xml',
             ],
    'application': True,
}