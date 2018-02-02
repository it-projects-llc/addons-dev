# -*- coding: utf-8 -*-
import logging
from odoo import fields
from odoo import models

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    screen = fields.Selection([
        ('kitchen', 'Kitchen'),
        ('waiter', 'Waiter')
    ], default='waiter', string='Specify Screen Type', required=True)

    cat_ids = fields.Many2many("pos.category", string="Kitchen Display Product Categories",
                                    help="The Product categories displayed on the kitchen screen")
    show_floors_plan = fields.Boolean("Show Floors Plan", default=False)
    show_all_kitchen_lines = fields.Boolean("Show All Kitchen Lines", default=False)
