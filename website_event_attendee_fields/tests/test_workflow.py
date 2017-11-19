# -*- coding: utf-8 -*-
import logging

from odoo import api
from odoo.tests.common import HttpCase


_logger = logging.getLogger(__name__)


class TestBackend(HttpCase):
    # Making post_install True requires to update demo data, because other modules may change them
    at_install = True
    post_install = False

    def test_base(self):
        # data in tours are saved (but not commited!) via different cursor. So, we have to use that one
        test_env = api.Environment(self.registry.test_cr, self.uid, {})

        registration_count_before = test_env['event.registration'].search_count([])

        self.phantom_js(
            '/event',

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".run('website_event_attendee_fields_test_tour_base', 1000)",

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".tours.website_event_attendee_fields_test_tour_base.ready",

            login='demo',
            timeout=200,
        )
        registration_count_after = test_env['event.registration'].search_count([])

        self.assertEqual(registration_count_before, registration_count_after - 2, "Amount of created registrations is not equal to 2")

        att_email = "att2@example.com"
        att_function = "JOB2"

        registration = test_env['event.registration'].search([], order='id desc', limit=1)

        self.assertEqual(registration.partner_id.email, att_email, "Latest registration doesn't have correct partner's email")
        self.assertEqual(registration.partner_id.function, att_function, "Latest registration doesn't have correct partner's Job")
