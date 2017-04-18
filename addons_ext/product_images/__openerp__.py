# -*- coding: utf-8 -*-

{
    'name': 'Product Images (Multiple Images)',
    'description': 'Add multiple images to products.',
    'version': '1.0',
    'website': 'https://hibou.io/',
    'author': 'Hibou Corp. <hello@hibou.io>',
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/product_images.xml',
        'views/website_product_images.xml',
    ],
    'category': 'Product',
    'depends': [
        'product',
        'website_sale',
    ],
}
