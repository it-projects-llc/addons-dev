# -*- coding: utf-8 -*-

# Copyright (C) 2019 Garazd Creation (<https://garazd.biz/>)
# Author: Yurii Razumovskyi (<support@garazd.biz>)
# License OPL-1 (https://www.odoo.com/documentation/user/legal/licenses/licenses.html#odoo-apps).

{
    'name': 'Staged Inventory',
    'version': '12.0.1.0.1',
    'category': 'Warehouse',
    'author': 'Garazd Creation',
    'website': "https://garazd.biz",
    'license': 'OPL-1',
    'summary': 'Stock Inventory in several stages',
    'description': """
    Inventory in several stages simultaneously by several employees.""",
    'depends': [
        'stock',
        'web_notify',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_inventory_views.xml',
        'views/stock_inventory_stage_views.xml',
    ],
    "qweb": [
        "static/src/xml/list_view_templates.xml"
    ],
    'price': 200.0,
    'currency': 'EUR',
    'application': False,
    'installable': True,
    'auto_install': False,
}
