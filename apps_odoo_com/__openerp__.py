# -*- coding: utf-8 -*-
# Copyright 2017 IT-Projects LLC (<https://it-projects.info>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Odoo App Store administration tool",
    "summary": "Tool to work with apps.odoo.com database via xmlrpc.",
    "version": "8.0.1.0.0",
    "category": "Extra Tools",
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
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter_data.xml",
        "views/menus.xml",
        "views/res_config_views.xml",
        "wizards/scan_repo_views.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
