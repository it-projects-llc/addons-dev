# -*- coding: utf-8 -*-
import logging
from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'restaurant.printer'

    network_printer = fields.Boolean(string='Network Printer')
