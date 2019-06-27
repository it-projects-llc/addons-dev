# -*- coding: utf-8 -*-
# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, _, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    inventory_adjustment = fields.Boolean('Inventory Mode')
