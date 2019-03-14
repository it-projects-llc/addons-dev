# -*- coding: utf-8 -*-
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    ask_for_sign = fields.Boolean(string='Ask To Sign', default=False)
    mandatory_ask_for_sign = fields.Boolean(string='Mandatory Ask To Sign', default=False)
    terms_to_sign = fields.Char(string='Terms & Conditions')

    @api.depends('ask_for_sign')
    @api.onchange('ask_for_sign')
    def _onchange_ask_for_sign(self):
        if not self.ask_for_sign:
            self.mandatory_ask_for_sign = False

    @api.model
    def send_to_esign_tab(self, channel_name, sub_channel, data):
        notifications = self.send_data_by_poll(channel_name, sub_channel, data)
        _logger.debug('EST notifications for %s: %s', self.ids, notifications)
        return

    @api.model
    def send_data_by_poll(self, channel_name, sub_channel, data):
        channel = '["%s","%s","%s"]' % (self._cr.dbname, channel_name, sub_channel)
        notifications = [[channel, data]]
        self.env['bus.bus'].sendmany(notifications)
        return notifications

    def open_esign_kiosk(self):
        return {
            'name': 'E-Sign Kiosk',
            'type': 'ir.actions.client',
            'tag': 'est_kiosk_mode',
            'target': 'fullscreen',
            'context': {
                'config_id': self.id,
                'terms_to_sign': self.terms_to_sign,
                'pos_name': self.name,
            },
        }


class ResPartner(models.Model):
    """Partners"""
    _inherit = 'res.partner'

    sign_attachment_id = fields.Many2one('ir.attachment', 'E-Sign')
