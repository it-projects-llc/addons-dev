# -*- coding: utf-8 -*-
import logging
from odoo import fields, models, api

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
    # show_all_kitchen_lines = fields.Boolean("Show All Kitchen Lines", default=False)
    custom_button_ids = fields.Many2many("pos.order.button", string="Custom Buttons")
    is_restaurant_installed = fields.Boolean(compute='_compute_state')

    def _compute_state(self):
        for r in self:
            r.is_restaurant_installed = r.is_module_installed('pos_restaurant')

    @api.model
    def is_module_installed(self, module_name=None):
        return module_name in self.env['ir.module.module']._installed()
