# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": """Integrate POS with WeChat mini-program""",
    "summary": """Integrate POS with WeChat mini-program""",
    "category": "Point of Sale",
    # "live_test_url": "",
    "images": [],
    "version": "11.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/GabbasovDinar",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "wechat_miniprogram",
        "qcloud_sms",
        "pos_longpolling",
        "pos_restaurant",
        "pos_order_note",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/wechat_security.xml",
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/template.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ],

    "auto_install": False,
    "installable": True,
}
