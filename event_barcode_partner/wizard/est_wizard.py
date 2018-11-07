# -*- coding: utf-8 -*-
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api
from datetime import datetime


class EsignatureTabSession(models.TransientModel):
    _name = 'est.session'

    user_id = fields.Many2one(
        'res.users', string='Responsible',
        required=True,
        index=True,
        readonly=True,
        states={'opening_control': [('readonly', False)]},
        default=lambda self: self.env.uid)

    event_id = fields.Many2one('event.event', string='Event', required=True)
    barcode_interface = fields.Integer(string='Barcode Interface Number', required=True)

    @api.multi
    def open_est_session(self):
        self.ensure_one()
        client_action = self.env.ref('event_barcode_partner.open_est_session_action')

        return {
            'name': 'E-Sign Kiosk',
            'type': 'ir.actions.client',
            'tag': 'est_kiosk_mode',
            'context': {
                'session_name': 'E-Sign Kiosk',
                'event_id': self.event_id.id,
                'barcode_interface': self.barcode_interface,
                # 'start_at': datetime.ToString("MM/dd/yyyy HH:mm:ss.fff", datetime.now()),
                'terms_to_sign': self.event_id.terms_to_sign,
            },
            'target': 'fullscreen',
        }
