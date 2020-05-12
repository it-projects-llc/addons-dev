# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Field Service Management Dashboard",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "category": "field_service_management",
    "license": "AGPL-3",
    "website": "http://www.serpentcs.com",
    "version": "10.0.1.0.0",
    "description": "This module is depends on field service management system",
    "depends": ["field_service_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/field_service_view.xml",
        "views/template_view.xml",
        "views/field_service_dashboard.xml",
    ],
    "qweb": [
        "static/src/xml/field_service_dashboard.xml",
    ],
    "installable": True,
    "auto_install": False
}
