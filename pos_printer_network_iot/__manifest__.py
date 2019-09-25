# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """IOT Network Printer""",
    "summary": """IOT Network Printer""",
    "category": "Point of Sale",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=12.0",
    "images": [],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Kolushov Alexandr",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/12.0/pos_printer_network_iot/",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "iot",
        "pos_printer_network",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/pos_printer_network_view.xml",
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

    # "demo_title": "IOT Network Printer",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "IOT Network Printer",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}
