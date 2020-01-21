# Copyright 2020 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": """Manufacturing Eurodesign""",
    "summary": """Custom features for Manufacturing""",
    "category": "Manufacturing",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=12.0",
    "images": [],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Denis Mudarisov",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/12.0/mrp_eurodesign/",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        'mrp_workorder',
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'security/ir.model.access.csv',
        'views/mrp_production_view.xml',
        'views/mrp_workorder_view.xml',
    ],
    "demo": [
    ],
    "qweb": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

    # "demo_title": "Manufacturing Eurodesign",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "Custom features for Manufacturing",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}
