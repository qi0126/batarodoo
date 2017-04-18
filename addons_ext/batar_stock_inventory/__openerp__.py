{
    'name': 'Batar Inventory Adjustments',
    'author': 'Xiao',
    'depends': ['batar_stock'],
    'data': [
        'views/data.xml',
        'views/stock_view.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
    'description': """
    extend inventory adjustments ,add the second uom
    """,
}