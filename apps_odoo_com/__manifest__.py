# Copyright 2017 IT-Projects LLC (<https://it-projects.info>)
# Copyright 2019 Anvar Kildebekov (<https://it-projects.info/team/fedoranvar>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Odoo App Store Admin tool",
    "summary": "Tool to work with apps.odoo.com database via xmlrpc.",
    "version": "12.0.1.0.0",
    "category": "Extra Tools",
    "images": ["images/main.jpg"],
    "website": "https://it-projects.info",
    "author": "IT-Projects LLC, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    # "pre_init_hook": "pre_init_hook",
    # "post_init_hook": "post_init_hook",
    # "post_load": "post_load",
    # "uninstall_hook": "uninstall_hook",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter_data.xml",
        "views/menus.xml",
        "views/res_config_views.xml",
        "views/stats_views.xml",
        "wizards/scan_repo_views.xml",
        "wizards/add_repos_views.xml",
        "wizards/update_data_views.xml",
    ],
    "demo": [
        "demo/apps_odoo_com.user.csv",
        "demo/apps_odoo_com.module.csv",
        "demo/apps_odoo_com.purchase.csv",
    ],
    "qweb": [
    ]
}
