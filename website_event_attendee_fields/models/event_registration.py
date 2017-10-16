# -*- coding: utf-8 -*-
from odoo import models, api


class EventRegistration(models.Model):
    _inherit = "event.registration"

    @api.model
    def _prepare_attendee_values(self, registration):
        """Extend it to pass partner values too (we remove them later in _prepare_partner)"""
        data = super(EventRegistration, self)._prepare_attendee_values(registration)
        partner_fields = self.env['res.partner']._fields
        data.update({key: registration[key] for key in registration.keys() if key in partner_fields})
        return data

    def _prepare_partner(self, vals):
        event = self.env['event.event'].browse(vals['event_id'])
        res = {}
        print 'vals BEFORE', vals
        partner_fields = self.env['res.partner']._fields
        for field in event.attendee_field_ids:
            fn = field.field_name
            if field.field_model == 'res.partner' or fn in partner_fields:
                res[fn] = vals.get(field.field_name)

            if fn not in self._fields:
                if fn in vals:
                    del vals[fn]

        print 'vals AFTER', vals
        print 'res', res
        return res
