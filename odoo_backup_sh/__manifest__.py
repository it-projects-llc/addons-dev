# Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """Odoo-backup.sh""",
    "summary": """Remote Backup Service""",
    "category": "Backup",
    # "live_test_url": "",
    "images": [],
    "version": "11.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Stanislav Krotov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/ufaks",
    "license": "LGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        'iap',
    ],
    "external_dependencies": {"python": ['boto3', 'botocore', 'pretty_bad_protocol'], "bin": []},
    "data": [
        'security/ir.model.access.csv',
        'views/odoo_backup_sh_templates.xml',
        'views/odoo_backup_sh_views.xml',
    ],
    'qweb': ['static/src/xml/dashboard.xml'],
    "demo": [
        'demo/tour_views.xml',
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
