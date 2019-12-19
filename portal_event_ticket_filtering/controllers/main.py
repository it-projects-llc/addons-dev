# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteEventControllerFilter(WebsiteEventController):

    @http.route(['/event/<model("event.event"):event>/register/<int:ticket_id>/'], type='http', auth="public", website=True)
    def event_register_filtered(self, event, ticket_id, **post):
        values = self.event_register(event, **post)
        ticket_id = event.event_ticket_ids.filtered(lambda e: e.id == ticket_id)
        values.qcontext.update({
            'tickets': len(ticket_id) and list(ticket_id) or [],
        })
        return values
