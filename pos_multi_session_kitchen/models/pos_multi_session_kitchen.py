# -*- coding: utf-8 -*-
import logging
from odoo import fields
from odoo import models

_logger = logging.getLogger(__name__)


class PosOrderLineState(models.Model):
    _name = "pos.order.line.state"

    name = fields.Char("Display Name")
    technical_name = fields.Char("Technical Name")
    type = fields.Selection([('stage', 'Stage'), ('tag', 'Tag')], default='stage')
    sequence = fields.Integer("Sequence")
    show_in_kitchen = fields.Boolean("Show State on Kitchen", default=True)
    show_for_waiters = fields.Boolean("Show the Button for Waiters", default=True)


class PosOrderLineButton(models.Model):
    _name = "pos.order.line.button"

    name = fields.Char("Button Label")

    background_color = fields.Char("Button Background Color")
    name_color = fields.Char("Button Name Color")

    show_for_waiters = fields.Boolean("Show the Button for Waiters")
    show_in_kitchen = fields.Boolean("Show the Button in Kitchen")

    next_state_id = fields.Many2one("pos.order.line.state", string="Next State",
                                    help="Next state to apply on clicking")

    condition_code = fields.Text(string='JS Code',
                                 help="The JS code is for check of button (show or hide the button in Orderline)."
                                      "Following variables can be used: \n\n * state - current state\n"
                                      "* product\n * quantity\n * price\n")


class PosKitchenCategorySettings(models.Model):
    _name = "pos.kitchen.category.settings"

    name = fields.Char(string="Name")
    button_ids = fields.Many2many("pos.order.line.button", string="Buttons")
    state_ids = fields.Many2many("pos.order.line.state", string="States")
