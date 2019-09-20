# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """Portal Debt History""",
    "summary": """Allows portal users to see their debt history""",
    "category": "Website",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=10.0",
    "images": ["images/debt_history1.png"],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Kolushov Alexandr",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/KolushovAlexandr",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "portal",
        "pos_debt_notebook",
        "website",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/website_portal_templates.xml",
        "data/test.xml",
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

    # "demo_title": "Portal Debt History",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "Allows portal users to see their debt history",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}
