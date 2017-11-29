# -*- coding: utf-8 -*-
{
    "name": """FACT Manager""",
    "summary": """FACT manager security group that not belong to group_erp_manager but has full access to account settings, partners, companies and products""",
    "category": "Access",
    # "live_test_url": "",
    "images": [],
    "version": "1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Ildar Nasyrov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/iledarn",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "sale",
        "access_settings_menu",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'security/accounting_manager_security.xml',
        'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'data/ir_values_data.xml',
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
