# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'restaurant.printer'

    network_printer = fields.Boolean(default=False, string='Network Printer', help="Check this box if this printer is Network printer")


class PosConfig(models.Model):
    _inherit = 'pos.config'

    receipt_printer_type = fields.Selection([
        ('usb_printer', 'USB Printer'),
        ('network_printer', 'Network Printer')], "Printer Type",
        default='usb_printer', required=True,
        help="Select the printer type you want to use receipt printing")
    receipt_network_printer_ip = fields.Char(default=False, string="Network Printer IP", help="The ip address of the network printer for receipt")

    @api.onchange('receipt_printer_type')
    def _onchange_receipt_printer_type(self):
        if self.receipt_printer_type == "usb_printer":
            self.receipt_network_printer_ip = False
