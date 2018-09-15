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
        "pos_multi_session_restaurant",
        "pos_order_note",
        "base_geolocalize",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/wechat_security.xml",
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/pos_wechat_miniprogram_view.xml",
        "views/template.xml",
        "views/pos_config_view.xml",
        "views/pos_restaurant_view.xml",
        "views/pos_multi_session_restaurant_view.xml",
        "wizard/qrcode.xml",
        "report/report_table_qrcode.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ],

    "auto_install": False,
    "installable": True,
}
