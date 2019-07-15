# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": """Sync Products in POS""",
    "summary": """Instant updates of the product data in POS""",
    "category": "Point of Sale",
    # "live_test_url": "http://apps.it-projects.info/shop/product/pos-product-sync?version=11.0",
    "images": [],
    "version": "11.0.2.0.1",
    "application": False,

    "author": "IT-Projects LLC, Kolushov Alexandr",
    "support": "pos@it-projects.info",
    "website": "https://it-projects.info/team/KolushovAlexandr",
    "license": "LGPL-3",
    "price": 49.00,
    "currency": "EUR",

    "depends": [
        "point_of_sale",
        "pos_longpolling",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/assets.xml",
        "views/pos_config.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

    # "demo_title": "Sync Product data in POS",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "pos-product-sync",
    # "demo_summary": "Update the product data in POS instantly",
    # "demo_images": [
    #     "images/pos_product_sync_main.png",
    # ]
}
