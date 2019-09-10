# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """Real Multi Website (eCommerce Comparison extension)""",
    "summary": """Real Multi Website (eCommerce Comparison extension)""",
    "category": "eCommerce",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=11.0",
    "images": [],
    "version": "11.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Kolushov Alexandr",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/{VERSION}/{TECHNICAL_NAME}/",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "website_multi_company_sale",
        "website_sale_comparison",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
    ],
    "demo": [
    ],
    "qweb": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

    # "demo_title": "Real Multi Website (eCommerce Comparison extension)",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "Real Multi Website (eCommerce Comparison extension)",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}
