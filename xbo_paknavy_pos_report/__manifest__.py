# -*- coding: utf-8 -*-
{
    "name": "Xbo PAk Navy pos Report",

    'version': '19.0.0.0',

    'summary': """Xbo PAk Navy pos Report""",

    'description': """Xbo PAk Navy pos Report""",

    'category': 'Pos',

    'author': "SelectaSol",

    'website': 'https://selectasol.com',

    "depends": ['base','point_of_sale'],

    "data": [
        'security/ir.model.access.csv',
        'report/multidays_profit_loss_template.xml',
        'report/pos_profit_loss_report_template.xml',
        'report/report_action.xml',
        'wizards/multidays_profit_loss_wizard.xml',
        # 'wizards/pos_profit_loss_wizard_views.xml',
    ],




    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,



}
