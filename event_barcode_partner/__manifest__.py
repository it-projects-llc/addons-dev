# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """Customised Event Barcode Interface""",
    "summary": """{SHORT module description for REAMDE and manifest}""",
    "category": "{MODULE_CATEGORY}",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=10.0",
    "images": [],
    "version": "10.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Kolushov Alexandr",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/KolushovAlexandr",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "event_barcode",
        "website_sign",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/assets.xml",
        "views/event_views.xml",
        "views/est_views.xml",
    ],
    "demo": [
    ],
    "qweb": [
        "static/src/xml/event_barcode_inherited.xml",
        "static/src/xml/est_templates.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

}
