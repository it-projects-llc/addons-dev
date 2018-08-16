# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging
import requests_mock

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from odoo.tests.common import HttpCase
from odoo import api


_logger = logging.getLogger(__name__)


class TestQCloudSMS(HttpCase):
    at_install = True
    post_install = True

    def setUp(self):
        super(TestQCloudSMS, self).setUp()
        self.phantom_env = api.Environment(self.registry.test_cr, self.uid, {})
        self.Message = self.phantom_env['qcloud.sms']
        self.partner = self.phantom_env.ref('base.res_partner_1')

        self.partner.write({
            'mobile': '+1234567890'
        })

        self.message_template = self.phantom_env['qcloud.sms.template'].create({
            'name': 'Test Template',
            'sms_type': '0'
        })

        # add patch
        self.requests_mock = requests_mock.Mocker(real_http=True)
        self.requests_mock.start()
        self.addCleanup(self.requests_mock.stop)

        patcher_possible_number = patch('phonenumbers.is_possible_number', wraps=lambda *args: True)
        patcher_possible_number.start()
        self.addCleanup(patcher_possible_number.stop)

        patcher_valid_number = patch('phonenumbers.is_valid_number', wraps=lambda *args: True)
        patcher_valid_number.start()
        self.addCleanup(patcher_valid_number.stop)

    def _patch_post_requests(self, url, response_json):
        self.requests_mock.register_uri('POST', url, json=response_json)

    def _send_simple_message(self, message):
        response_json = {
            "result": 0,
            "errmsg": "OK",
            "ext": "",
            "fee": 1,
            "sid": "xxxxxxx"
        }
        url = 'https://yun.tim.qq.com/v5/tlssmssvr/sendsms'
        self._patch_post_requests(url, response_json)

        return self.Message.send_message(message, self.partner.id, template_id=self.message_template.id)

    def test_send_message(self):
        message = "Your login verification code is 1234, which is valid for 2 minutes." \
                  "If you are not using our service, ignore the message."

        response = self._send_simple_message(message)
        self.assertEquals(response.get('result'), 0, 'Could not send message')
