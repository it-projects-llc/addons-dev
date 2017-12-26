# -*- coding: utf-8 -*-
{
    "name": """Insurance Broker Car Pricing""",
    "summary": """Basic Pricing for Car Insurance Brokers""",
    "category": "Sales",
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
        "fleet",
        "sale_start_end_dates",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "data/product_data.xml",
        "data/product.product.csv",
        "data/ir_values_data.xml",
        "security/sales_team_security.xml",
        'security/ir.model.access.csv',
        "views/fleet_view.xml",
        "views/insurance_broker_car_pricing_view.xml",
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
