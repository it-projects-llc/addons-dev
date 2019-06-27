# Copyright 2019 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """Backups into Dropbox""",
    "summary": """Your backups into Dropbox""",
    "category": "Backup",
    # "live_test_url": "",
    "images": ['images/backup_dropbox.jpg'],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/GabbasovDinar",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "odoo_backup_sh",
    ],
    "external_dependencies": {"python": ["dropbox"], "bin": []},
    "data": [
        "views/odoo_backup_sh_views.xml",
        "views/odoo_backup_sh_dropbox_templates.xml",
        "views/res_config_settings_views.xml",
    ],
    "qweb": [
        "static/src/xml/dashboard.xml"
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
