# -*- coding: utf-8 -*-

# Copyright (C) 2018 Razumovskyi Yurii <GarazdCreation@gmail.com>
# License OPL-1 (https://www.odoo.com/documentation/user/legal/licenses/licenses.html#odoo-apps).

{
    'name': 'Garazd Loyalty Program',
    'version': '12.0.1.0.1',
    'category': 'Sales',
    'author': 'Garazd Creation',
    'website': "https://garazd.biz",
    'license': 'OPL-1',
    'summary': """
        Loyalty Program for Sales
    """,
    'description': 'Manage Loyalty Program for Customers',
    'depends': [
        'base',
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/loyalty_security.xml',
        'views/garazd_loyalty_templates.xml',
        'views/garazd_loyalty_views.xml',
        'views/res_config_views.xml',
        'views/res_partner_views.xml',
        'views/pos_config_views.xml',
     ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
