# -*- coding: utf-8 -*-
# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": """Product Label""",
    "summary": """Use different labels of products for reports""",
    "category": "Reporting",
    # "live_test_url": "",
    "images": [],
    "version": "10.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/GabbasovDinar",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "product",
        "report",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "data/product_label_data.xml",
        "security/ir.model.access.csv",
        "wizard/product_label_wizard_view.xml",
        "report/product_label_report_template.xml",
        "report/product_label_report.xml",
        "views/product_template_view.xml",
        "views/product_label_view.xml",
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
