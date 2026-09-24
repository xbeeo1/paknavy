# -*- coding: utf-8 -*-
{
    'name': 'POS Restrict Zero Quantity Location Wise',
    'version': '19.0.0.0',
    'category': 'Point of Sale',
    'summary': 'Point Of Sale Restrict Zero Quantity Location Wise',
    'description' :"""
       The Point Of Sale Restrict Zero Quantity Location Wise
    """,
    'author': "Musadiq Fiaz",

    'website': 'https://musadiqfiaz.com',
    'depends': ['base','point_of_sale'],
    'data': [
        'views/pos_config_view.xml',
    ],
    'assets': {
            'point_of_sale._assets_pos': [
                'ssol_pos_restrict_neg_qty_loc/static/src/**/*',

                    ],
    },
    'license': 'LGPL-3',
}
