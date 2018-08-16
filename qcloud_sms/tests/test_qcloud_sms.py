# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

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
        self.partner_1 = self.phantom_env.ref('base.res_partner_1')
        self.partner_2 = self.phantom_env.ref('base.res_partner_2')

        self.partner_1.write({
            'mobile': '+1234567890'
        })

        self.partner_2.write({
            'mobile': '+1987654320'
        })

        self.message_template = self.phantom_env['qcloud.sms.template'].create({
            'name': 'Test Template',
            'sms_type': '0'
        })

        # add patch
        patcher_possible_number = patch('phonenumbers.is_possible_number', wraps=lambda *args: True)
        patcher_possible_number.start()
        self.addCleanup(patcher_possible_number.stop)

        patcher_valid_number = patch('phonenumbers.is_valid_number', wraps=lambda *args: True)
        patcher_valid_number.start()
        self.addCleanup(patcher_valid_number.stop)

    def _patch_post_requests(self, url, response_json):

        def api_request(req, httpclient=None):
            _logger.debug("Request data: req - %s, httpclient - %s", req, httpclient)
            return response_json

        patcher = patch('qcloudsms_py.util.api_request', wraps=api_request)
        patcher.start()
        self.addCleanup(patcher.stop)

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

        return self.Message.send_message(message, self.partner_1.id, template_id=self.message_template.id)

    def test_send_message(self):
        message = "Your login verification code is 1234, which is valid for 2 minutes." \
                  "If you are not using our service, ignore the message."

        response = self._send_simple_message(message)
        self.assertEquals(response.get('result'), 0, 'Could not send message')

    def _send_group_message(self, message):
        response_json = {
            "result": 0,
            "errmsg": "OK",
            "ext": "",
            "fee": 1,
            "sid": "xxxxxxx"
        }
        url = 'https://yun.tim.qq.com/v5/tlssmssvr/sendsms'
        self._patch_post_requests(url, response_json)

        return self.Message.send_group_message(message, [self.partner_1.id, self.partner_2.id], template_id=self.message_template.id)

    def test_send_group_message(self):
        message = "Discount for all products 50%!"
        response = self._send_group_message(message)
        self.assertEquals(response.get('result'), 0, 'Could not send message')
