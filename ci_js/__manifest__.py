# Copyright 2018 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """CI JS""",
    "summary": """CI addonn for Odoo to make tours""",
    "category": "Extra Tools",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=10.0",
    "images": [],
    "version": "10.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Denis Mudarisov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/trojikman",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    # "depends": [
    #     "{DEPENDENCY1}",
    #     "{DEPENDENCY2}",
    # ],
    # "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/ir.model.access.csv",
        "views/ci_js_view.xml",
        "data/data.xml"
    ],
    # ],
    # "qweb": [
    #     "static/src/xml/{QWEBFILE1}.xml",
    # ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

    # "demo_title": "{CI JS}",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "{CI addonn for Odoo to make tours}",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}
