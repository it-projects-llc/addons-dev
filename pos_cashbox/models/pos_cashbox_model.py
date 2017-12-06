# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = 'pos.session'

    iface_cashdrawer = fields.Boolean(related='config_id.iface_cashdrawer')
    proxy_ip = fields.Char(related='config_id.proxy_ip')

    @api.multi
    def open_backend_cashbox(self):
        pass
