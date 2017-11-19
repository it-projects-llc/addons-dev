# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    @api.model
    def create(self, vals):
        event = self.env['event.event'].browse(vals['event_id'])

        partner = vals.get('partner_id')
        if partner:
            if event.create_partner:
                partner = self.env['res.partner'].browse(partner)
                if vals.get('email') != partner.email:
                    partner_by_email = self.env['res.partner'].search([('email', '=ilike', vals.get('email'))], limit=1)
                    if partner_by_email:
                        # Set value to don't apply extension of create method from partner_event.
                        # Basically, it's needed to don't update phone and name in vals by partner_event and do it here instead. See below
                        vals['attendee_partner_id'] = partner_by_email.id

        res = super(EventRegistration, self).create(vals)

        if res.attendee_partner_id:
            # be sure, that name and phone in registration are ones from Attendee and not from Contact. See README for more details
            res.name = res.attendee_partner_id.name
            res.phone = res.attendee_partner_id.phone

        if res.event_id.attendee_signup and res.partner_id:
            login = res.partner_id.email
            user = self.env['res.users']\
                       .search([('login', '=ilike', login)])
            if not user:
                user = self.env['res.users']\
                           ._signup_create_user({
                               'login': login,
                               'partner_id': res.partner_id.id,
                           })
                user.partner_id.signup_prepare()

        return res
