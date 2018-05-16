# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Kingrun Customization',
    'version': '10.0.1.0.0',
    'description': """
        Kingrun Customization
    """,
    'author': 'BizzAppDev',
    'website': 'https://www.bizzappdev.com',
    'depends': [
        'sale',
        'calendar',
        'point_of_sale',
        'account_accountant',
        'purchase',
        'board',
        'mrp',
        'stock',
        'sale_mrp',
    ],
    'data': [
        'security/mrp_security_view.xml',
        'view/mrp_view.xml',
        'view/menu_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
