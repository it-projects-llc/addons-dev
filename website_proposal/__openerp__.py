# -*- coding: utf-8 -*-
{
    'name': 'Website proposal',
    'version': '1.0.0',
    'author': 'IT-Projects LLC, Ivan Yelizariev',
    'license': 'LGPL-3',
    'category': 'Website',
    'website': 'https://yelizariev.github.io',
    'description': """
Technical module to create web-based proposals for accepting (signing) by partner. E.g. confirmation different documents in leads.

Also module allows convert proposal to pdf.
    """,
    'depends': ['website',
                'report',
                'email_template',
                'hr',
                'web_logo',
                'web',
                'is_employee',
                ],
    'data': [
        'views.xml',
        'report.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'installable': False,
    'auto_install': False,
    'application': False,
}
