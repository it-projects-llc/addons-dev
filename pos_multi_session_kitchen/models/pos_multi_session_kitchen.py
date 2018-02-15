# -*- coding: utf-8 -*-
import logging
from odoo import fields
from odoo import models

_logger = logging.getLogger(__name__)


class PosOrderLineState(models.Model):
    _name = "pos.order.line.state"

    name = fields.Char("Display Name", required=True)
    technical_name = fields.Char("Technical Name", required=True)
    type = fields.Selection([('state', 'State'), ('tag', 'Tag')], default='state')
    sequence = fields.Integer("Sequence", default=0)
    show_in_kitchen = fields.Boolean("Show State on Kitchen", default=True)
    show_for_waiters = fields.Boolean("Show the Button for Waiters", default=True)
    sound_signal = fields.Boolean("Sound Signal", help="The sound signal about a state change", default=False)


class PosOrderLineButton(models.Model):
    _name = "pos.order.line.button"

    name = fields.Char("Button Label", required=True)
    background_color = fields.Char("Button Background Color")
    name_color = fields.Char("Button Name Color")
    show_for_waiters = fields.Boolean("Show the Button for Waiters")
    show_in_kitchen = fields.Boolean("Show the Button in Kitchen")
    next_state_id = fields.Many2one("pos.order.line.state", string="Next State",
                                    help="Next state to apply on clicking")
    condition_code = fields.Text(string='Python Code',
                                 help="The Python code is for check of button (show or hide the button in Orderline)."
                                      "Following variables can be used: \n\n * state - current state\n"
                                      "* product\n * quantity\n * price\n")
    action_close = fields.Boolean(string="Close action",
                                  help="Stop the timer and remove from the kitchen", defaul=False)


class PosOrderLineState(models.Model):
    _name = "pos.order.tag"
    _order = "priority, technical_name"

    name = fields.Char("Display Name", required=True)
    name_color = fields.Char("Tag Name Color")
    background_color = fields.Char("Tag Background Color")
    technical_name = fields.Char("Technical Name", required=True)
    priority = fields.Integer("Priority", default=5)


class PosOrderButton(models.Model):
    _name = "pos.order.button"

    name = fields.Char("Button Label", required=True)
    background_color = fields.Char("Button Background Color")
    name_color = fields.Char("Button Name Color")
    remove_tag_id = fields.Many2one("pos.order.tag", string="Remove Tag", help="The tag to remove on clicking")
    next_tag_id = fields.Many2one("pos.order.tag", string="Apply Tag", help="Next tag to apply on clicking")


class PosKitchenCategorySettings(models.Model):
    _name = "pos.kitchen.category.settings"

    name = fields.Char(string="Name")
    button_ids = fields.Many2many("pos.order.line.button", string="Buttons")
    state_ids = fields.Many2many("pos.order.line.state", string="States")
