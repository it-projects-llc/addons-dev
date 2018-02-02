# -*- coding: utf-8 -*-
import logging
from odoo import fields
from odoo import models

_logger = logging.getLogger(__name__)


class PosCategory(models.Model):
    _inherit = "pos.category"

    settings_id = fields.Many2one("pos.kitchen.category.settings", string='Settings')
