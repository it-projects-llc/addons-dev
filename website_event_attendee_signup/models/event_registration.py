# -*- coding: utf-8 -*-
from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    agent_id = fields.Many2one(
        'res.users', string='Agent',
        states={'done': [('readonly', True)]},
        help="A person who purchased the registration",
    )

    @api.model
    def create(self, vals):
        event = res['event.event'].browse(vals['event_id'])
        if event.create_partner:
            partner = vals.get('partner_id'):
            if partner:
                partner = self.env['res.partner'].browse(partner)
            if partner and vals.get('email') != partner.email:
                # delete it to force event_partner module to create new partner for this attendee
                del vals['partner_id']

        res = super(EventRegistration, self).create(vals)

        if res.event_id.attendee_signup and res.partner_id:
            user = self.env['res.users'].create({'partner_id': res.partner_id.id})
            user.signup_prepare()
            template = self.env.ref(
            res.partner_id.with_context(user=user).message_post_with_template(template.id, composition_mode='comment')

        return res
