# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    "name": "Digital Signature approval",
    "version": "1.0",
    'depends': ['purchase','account','sale','project_subtask',],
    "description": """
        Get digital approval by manager on each category of document.

    """,
    'data': [
        'views/import_lib.xml',
        'wizard/digital_sign_view.xml',
        # 'views/purchase_order.xml',
        # 'views/account_invoice.xml',
        # 'views/sale_order.xml',
        'views/project_task_view.xml',
    ],
    'website': "contact@hartechnologies.com",
    "price": "45.00",
    "currency":"EUR",
    'license':'AGPL-3',
    "images":['static/description/Banner.png'],
    'qweb': ['static/xml/signature_template.xml'],
    'installable': True,
    'auto_install': False,
}
