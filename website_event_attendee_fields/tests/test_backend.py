# -*- coding: utf-8 -*-
import logging

from . import common


_logger = logging.getLogger(__name__)


class TestBackend(common.TestCase):

    def test_coverage(self):

        country_field = self.env.ref('website_event_attendee_fields.attendee_field_country_id')
        self.event.write({
            'attendee_field_ids': [(6,0,[
                self.env.ref('website_event_attendee_fields.attendee_field_name').id,
                self.env.ref('website_event_attendee_fields.attendee_field_email').id,
                self.env.ref('website_event_attendee_fields.attendee_field_phone').id,
                country_field.id,
            ])]
        })
        # cover name_get()
        _logger.info('name_get for country field: %s', country_field.display_name)

        country_field.domain = "[('code', '=', 'RU')]"

        self.assertEqual(1, len(country_field.get_select_options()))

        country_field.domain = False
        self.assertTrue(1 < len(country_field.get_select_options()))
