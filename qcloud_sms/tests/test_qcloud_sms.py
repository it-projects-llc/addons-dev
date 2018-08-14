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

        self.requests_mock = requests_mock.Mocker(real_http=True)
        self.requests_mock.start()
        self.addCleanup(self.requests_mock.stop)

    def _patch_post_requests(self, url, data, response_json):
        self.requests_mock.register_uri('POST', url, request_headers=data, json=response_json)

    def _send_simple_message(self, data):
        response_json = {
            "result": 0,
            "errmsg": "OK",
            "ext": "",
            "fee": 1,
            "sid": "xxxxxxx"
        }
        base_url = 'https://yun.tim.qq.com/v5/tlssmssvr/sendsms'
        self._patch_post_requests(base_url, data, response_json)
        return self.Message.send_message(data)

    def test_send_message(self):
        # sms_type: 0 - normal SMS, 1 - marketing SMS
        data = {
            'sms_type': 0,
            'country_code': 0,
            'phone_number': 123456789,
            'msg': "Your verification code: 1234"
        }
        response = self._send_simple_message(data)
        self.assertEquals(response.result, 0, 'Could not send message')
