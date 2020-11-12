# -*- coding: utf-8 -*-


{
    'name': 'sta',
    'version': '1.0',
    'category': 'Hidden',
    'sequence': 6,
    'summary': 'Modulo STA',
    'description': """

""",
    'depends': ['purchase','product','mrp','stock'],
    'data': [
        'views/reporte_inventario_produccion.xml',
        'views/report.xml',
        'views/product_views.xml',
        'views/account_view.xml',
        'views/stock_picking_views.xml',
        'views/purchase_views.xml',
        'views/stock_quant_views.xml',
        'views/sale_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
