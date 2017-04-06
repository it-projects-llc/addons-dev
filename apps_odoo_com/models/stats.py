# -*- coding: utf-8 -*-
# Copyright 2017 IT-Projects LLC (<https://it-projects.info>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openerp import models, fields, api


class Purchase(models.Model):
    """Copy of records loempia.module.purchase from apps.odoo.com"""

    _name = 'apps_odoo_com.purchase'

    #id = fields.Integer(readonly=True)
    purchase_order_ref = fields.Char(readonly=True)
    #display_name = fields.Char(readonly=True)
    user_id = fields.Many2one('apps_odoo_com.user', string="Buyer", readonly=True, index=True)
    product_id = fields.Char(readonly=True)
    referrer_module_id = fields.Many2one('apps_odoo_com.module', string="Referrer Module", readonly=True)
    __last_update = fields.Datetime(readonly=True)
    order_id = fields.Char(readonly=True)
    price_unit = fields.Float(readonly=True)
    price = fields.Float(readonly=True)
    order_name = fields.Char(readonly=True)
    state = fields.Char(readonly=True)
    #module_maintainer_id = fields.Char(readonly=True)
    module_id = fields.Many2one('apps_odoo_com.module', string="Module", readonly=True)
    date_order = fields.Char(readonly=True)
    quantity = fields.Float(readonly=True)

"""
"purchase_order_ref": false
"display_name": "loempia.module.purchase,39854"
"user_id": [180092 "Werner Amann"]
"product_id": 1645
"referrer_module_id": [21110 "Mail Base"]
"__last_update": "2017-04-03 19:40:44"
"order_id": 172127
"price_unit": 9.0
"price": 9.0
"order_name": "SO2017/171883"
"state": "confirmed"
"module_maintainer_id": [59928 "Ivan Elizaryev"]
"module_id": [21110 "Mail Base"]
"date_order": "2017-04-03 17:40:24"
"id": 39854
"quantity": 1.0}
"""
