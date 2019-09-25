# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class RestaurantPrinter(models.Model):
    _inherit = 'restaurant.printer'

    printer_proxy_ip = fields.Char('IP Address', help="IP Address of PosBox if it's USB Printer"
                                                      "or IP Address Network Printer otherwise")
    proxy_ip = fields.Char('IP Address', compute='_compute_proxy_ip')

    @api.depends('printer_proxy_ip', 'network_printer', 'iotbox_id', 'iotbox_id.ip')
    def _compute_proxy_ip(self):
        for record in self:
            if record.network_printer and record.printer_proxy_ip:
                record.proxy_ip = record.printer_proxy_ip
            else:
                record.proxy_ip = record.iotbox_id.ip
