# -*- coding: utf-8 -*-
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api
import uuid

import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_event_id = fields.Many2one('event.event', string='Event', default=False)
    show_only_tickets = fields.Boolean(string='Only Tickets', help='Show only ticket products', default=False)
    ask_for_rfid = fields.Boolean(string='Mandatory RFID',
                                  help='Ask for RFID to process attendee', store=True)
    web_url = fields.Char(
        default=lambda self: self.env["ir.config_parameter"].get_param("web.base.url") + "/web#id=")


class ResPartner(models.Model):
    _inherit = 'res.partner'


class EventEvent(models.Model):
    _inherit = 'event.event'

    mandatory_rfid = fields.Boolean('RFID', default=True)
    bracelet_ids = fields.One2many('event.bracelet', 'event_id', string='Bracelets')


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.model
    def _get_random_token(self):
        """Generate a 20 char long pseudo-random string of digits

        Used for barcode generation, UUID4 makes the chance of a collision
        (unicity constraint) highly unlikely.
        Using the int version is a longer string than hex but generates a more
        compact barcode when using digits only (Code128C instead of Code128A).
        Keep only the first 8 bytes as a 16 bytes barcode is not readable by all
        barcode scanners.
         """
        return str(int(uuid.uuid4().bytes[:8].encode('hex'), 16))

    barcode = fields.Char(default=_get_random_token, copy=False)
    rfid = fields.Char(related='partner_id.barcode', string='RFID', copy=False)
    bracelet_id = fields.One2many('event.bracelet', 'event_registration_id', string='Bracelet')

    @api.model
    def create_from_ui(self, attendee):
        """ create or modify a attendee from the point of sale ui.
            partner contains the partner's fields. """
        attendee_id = attendee.pop('id', False)
        if attendee_id:  # Modifying existing partner
            attendee_id = self.browse(attendee_id)
            attendee_id.write(attendee)
        else:
            attendee_id = self.create(attendee)
        if 'rfid' in attendee:
            self.env['event.bracelet'].create({
                'rfid': attendee['rfid'],
                'session_id': attendee['session_id'],
                'event_registration_id': attendee_id.id,
                'event_id': attendee['event_id'],
            })
        return attendee_id.id

    @api.multi
    def register_attendee_from_ui(self):
        self.ensure_one()
        self.button_reg_close()
        return self.id

    @api.multi
    def send_updates(self):
        channel_name = "pos_attendee_update"
        data = {'message': 'update_attendee', 'attendees': self.ids}
        self.env['pos.config'].send_to_all_poses(channel_name, data)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _process_order(self, pos_order):
        order = super(PosOrder, self)._process_order(pos_order)
        if order.config_id.pos_event_id and order.partner_id and order.lines.mapped('product_id.event_ticket_ids'):
            attendee = self.env['event.registration'].create({
                'event_id': order.config_id.pos_event_id.id,
                'partner_id': order.partner_id.id,
                'attendee_partner_id': order.partner_id.id,
                'origin': order.pos_reference,
                'event_ticket_id': order.lines.product_id.event_ticket_ids[0].id,
                'email': order.partner_id.email,
                'name': order.partner_id.name,
                'state': 'open',
            })
            attendee.send_updates()
        return order


class BraceletInfo(models.Model):
    _name = "event.bracelet"

    rfid = fields.Char(string='RFID', required=True)
    creation_time = fields.Datetime(string='Latest Connection', default=lambda self: fields.Datetime.now(),
                                    required=True, readonly=True)
    session_id = fields.Many2one('pos.session', string='POS Session')
    config_id = fields.Many2one('pos.config', related='session_id.config_id', string='POS', store=True)
    event_id = fields.Many2one('event.event', string='Event', required=True)

    event_registration_id = fields.Many2one('event.registration', string='Registration', required=True)
    event_ticket_id = fields.Many2one('event.event.ticket', related='event_registration_id.event_ticket_id',
                                      store=True, string='Ticket')
