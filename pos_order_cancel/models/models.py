# -*- coding: utf-8 -*-
from odoo import fields, models


class PosCancelledReason(models.Model):
    _name = "pos.cancelled_reason"

    number = fields.Integer(string="Number")
    name = fields.Char(string="Reason")
