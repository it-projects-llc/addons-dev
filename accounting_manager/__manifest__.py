# -*- coding: utf-8 -*-
{
    "name": """Accounting manager""",
    "summary": """FACT manager security group that not belong to group_erp_manager but has full access to account settings""",
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
        "product",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'security/accounting_manager.xml',
        'security/ir.model.access.csv',
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
