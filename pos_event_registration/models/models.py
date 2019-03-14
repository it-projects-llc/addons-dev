# -*- coding: utf-8 -*-
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api
import random
import string

import logging

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_event_set_id = fields.Many2one('pos.event.set', string='Event Set', default=False)
    show_only_tickets = fields.Boolean(string='Only Tickets', help='Show only ticket products', default=False)
    web_url = fields.Char(default=lambda self: self.env["ir.config_parameter"].get_param("web.base.url") + "/web#id=")


class PosEvent(models.Model):
    _name = 'pos.event.set'
    _description = 'Set relation between products and tickets, allows to sell tickets for different events'

    name = fields.Char('Name', required=True)
    pos_ticket_ids = fields.One2many('pos.event.ticket', 'pos_event_set_id', string="POS Ticket")
    pos_config_id = fields.One2many('pos.config', 'pos_event_set_id', string="POS", readonly=True)


class PosEventTicket(models.Model):
    _name = 'pos.event.ticket'
    _description = 'Set relation betwee products and tickets, allows to sell tickets for different events'

    _sql_constraints = [
        ('product_id_unique', 'unique (product_id)', "Ticket and Product Must Be Unique!"),
    ]

    pos_event_set_id = fields.Many2one('pos.event.set', string='Event Set', default=False)

    product_id = fields.Many2one('product.product', string="Product", required=True)
    ask_for_rfid = fields.Boolean(string='Mandatory RFID', help='Ask for RFID to process attendee', store=True)

    event_id = fields.Many2one('event.event', string="Event")
    ticket_id = fields.Many2one('event.event.ticket', string="Ticket", required=True)
    name = fields.Char('Name', compute="_compute_name", readonly=1)

    @api.onchange('event_id')
    def _onchange_event_id(self):
        return {'domain': {'ticket_id': [('event_id', '=', self.event_id.id)]}}

    @api.multi
    @api.depends('ticket_id')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.event_id and rec.ticket_id and rec.event_id.name + ": " + rec.ticket_id.name or ''


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
        return ''.join(random.choice(string.digits) for _ in range(20))

    barcode = fields.Char(default=_get_random_token, copy=False)
    rfid = fields.Char(related='attendee_partner_id.barcode', string='RFID', copy=False)
    bracelet_id = fields.One2many('event.bracelet', 'event_registration_id', string='Bracelet')

    @api.model
    def create_from_ui(self, attendee):
        """ create or modify a attendee from the point of sale ui.
            partner contains the partner's fields. """
        _logger.info("Creating Bracelet with vals %s", attendee)
        attendee_id = attendee.pop('id', False)
        if attendee_id:  # Modifying existing attendee
            attendee_id = self.browse(attendee_id)
            attendee_id.write(attendee)
        else:
            attendee_id = self.create(attendee)
        if 'rfid' in attendee:
            attendee_partner_id = attendee_id.attendee_partner_id
            attendee_partner_id.barcode = attendee['rfid']
            if not attendee_partner_id:
                Partner = self.env['res.partner']
                attendee_partner_id = Partner.search([
                    ('email', '=ilike', attendee_id.email)
                ], limit=1)
                if not attendee_partner_id:
                    vals = {
                        'email': attendee_id.email,
                        'name': attendee_id.name,
                        'phone': attendee_id.phone,
                    }
                    attendee_partner_id = Partner.sudo().create(
                        self._prepare_partner(vals))
                attendee_id.write({
                    'attendee_partner_id': attendee_partner_id.id,
                })
            self.env['event.bracelet'].create({
                'rfid': attendee['rfid'],
                'session_id': attendee['session_id'],
                'event_registration_id': attendee_id.id,
                'event_id': attendee_id.event_id.id,
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

        pos_event_set_id = order.config_id.pos_event_set_id
        partner_id = order.partner_id
        order_product_ids = order.lines.mapped('product_id')
        event_product_ids = pos_event_set_id.mapped('pos_ticket_ids').mapped('product_id')
        order_event_product_ids = order_product_ids & event_product_ids
        if pos_event_set_id and partner_id and order_event_product_ids:
            for line in order.lines:
                product_id = line.product_id
                if product_id.id not in event_product_ids.ids:
                    continue
                qty = int(line.qty)
                ticket = self.env['pos.event.ticket'].search([('pos_event_set_id', '=', pos_event_set_id.id),
                                                              ('product_id', '=', product_id.id)])[0]
                for i in range(int(qty)):
                    name = not i and partner_id.name or partner_id.name + ' person ' + str(i + 1)
                    vals = {
                        'event_id': ticket.event_id.id,
                        'partner_id': partner_id.id,
                        'attendee_partner_id': partner_id.id,
                        'origin': order.pos_reference,
                        'event_ticket_id': ticket.ticket_id.id,
                        'email': partner_id.email,
                        'name': name,
                        'state': 'open',
                    }
                    _logger.info("Creating Attendee with vals %s", vals)

                    attendee = self.env['event.registration'].create(vals)
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
    attendee_partner_id = fields.Many2one('res.partner', string='Partner', readonly=True,
                                          related='event_registration_id.attendee_partner_id')
