# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """HeatMap Widget""",
    "summary": """Use new HeatMap widget to display your records""",
    "category": "Extra Tools",
    "images": [],
    "version": "11.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/GabbasovDinar",
    "license": "LGPL-3",
    "price": 49.00,
    "currency": "EUR",

    "depends": [
        "web",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/web_widget_heatmap_template.xml",
    ],
    "demo": [
    ],
    "qweb": [
        "static/src/xml/base.xml"
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
