# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteEventControllerExtended(WebsiteEventController):
    @http.route()
    def registration_confirm(self, event, **post):
        """Check that threre are no email duplicates.
        There is a check on frontend, but that is easy to get around."""
        registrations = self._process_registration_details(post)
        emails = [r.get("email", "").strip() for r in registrations]
        assert len(emails) == len(set(emails))
        return super(WebsiteEventControllerExtended, self).registration_confirm(event, **post)

    @http.route(['/website_event_attendee_fields/check_email'], type='json', auth="public", methods=['POST'], website=True)
    def check_email(self, event_id, email):
        partner = request.env['res.partner'].sudo().search([
            ('email', '=', email),
        ], limit=1)
        if not partner:
            return {}

        registration = request.env['event.registration'].sudo().search([
            ('event_id', '=', event_id),
            ('partner_id', '=', partner.id),
            ('state', '=', 'open'),
        ])
        if registration:
            return {
                'email_not_allowed': _('This email address is already signed up for the event')
            }

        event = request.env['event.event'].sudo().browse(event_id)
        known_fields = []
        for f in event.attendee_field_ids:
            if f.field_name == 'email':
                continue
            if getattr(partner, f.field_name):
                known_fields.append(f.field_name)

        return {
            'known_fields': known_fields
        }
