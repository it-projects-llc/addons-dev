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
        self.user = self.phantom_env.user
        self.partner = self.user.partner_id

        self.partner.write({
            'mobile': '+1234567890'
        })

        self.Order = self.phantom_env['pos.miniprogram.order']

        self.product1 = self.phantom_env['product.product'].create({
            'name': 'Product1',
        })
        self.product2 = self.phantom_env['product.product'].create({
            'name': 'Product2',
        })

        self.lines = [
            {
                "product_id": self.product1.id,
                "name": "Product 1 Name",
                "quantity": 1,
                "price": 1,
                "category": "123456",
                "description": "翻译服务器错误",
            },
            {
                "product_id": self.product2.id,
                "name": "Product 2 Name",
                "quantity": 1,
                "price": 2,
                "category": "123456",
                "description": "網路白目哈哈",
            }
        ]

        # fake values for a test
        table = self.phantom_env.ref('pos_restaurant.table_01')

        self.create_vals = {
            'note': 'This is test Order note',
            'table_id': table.id,
            'guests': 4
        }

        # add patch
        patcher_possible_number = patch('phonenumbers.is_possible_number', wraps=lambda *args: True)
        patcher_possible_number.start()
        self.addCleanup(patcher_possible_number.stop)

        patcher_valid_number = patch('phonenumbers.is_valid_number', wraps=lambda *args: True)
        patcher_valid_number.start()
        self.addCleanup(patcher_valid_number.stop)

        patcher = patch('wechatpy.WeChatPay.check_signature', wraps=lambda *args: True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _check_verification_code(self):
        code = self.user.verification_code
        return self.user.check_verification_code(code)

    def _patch_post_requests(self, response_json, patch_url):

        def api_request(url=None, req=None, httpclient=None):
            _logger.debug("Request data: req - %s, httpclient - %s", req, httpclient)
            return response_json

        patcher = patch(patch_url, wraps=api_request)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _sms_template_mobile_number_verification(self, mobile, template_id):
        response_json = {
            "result": 0,
            "errmsg": "OK",
            "ext": "",
            "fee": 1,
            "sid": "xxxxxxx"
        }
        patch_url = 'qcloudsms_py.util.api_request'
        self._patch_post_requests(response_json, patch_url)

        return self.user.sms_template_mobile_number_verification(mobile, template_id)

    def _sms_mobile_number_verification(self, mobile):
        response_json = {
            "result": 0,
            "errmsg": "OK",
            "ext": "",
            "fee": 1,
            "sid": "xxxxxxx"
        }
        patch_url = 'qcloudsms_py.util.api_request'
        self._patch_post_requests(response_json, patch_url)

        return self.user.sms_mobile_number_verification(mobile)

    def _create_from_miniprogram_ui(self, create_vals, lines):
        post_result = {
            'pay/unifiedorder': {
                'trade_type': 'JSAPI',
                'result_code': 'SUCCESS',
                'prepay_id': 'qweqweqwesadsd2113',
                'nonce_str': 'wsdasd12312eaqsd21q3'
            }
        }

        def post(url, data):
            _logger.debug("Request data for %s: %s", url, data)
            return post_result[url]

        # patch wechat
        patcher = patch('wechatpy.pay.base.BaseWeChatPayAPI._post', wraps=post)
        patcher.start()
        self.addCleanup(patcher.stop)

        return self.phantom_env['pos.miniprogram.order'].create_from_miniprogram_ui(lines, create_vals)

    def test_sms_mobile_number_verification(self):
        mobile = '+1234567890'
        response = self._sms_mobile_number_verification(mobile)
        self.assertEquals(response.get('result'), 0, 'Could not send message')
        res = self._check_verification_code()
        self.assertTrue(res.get('result'), res.get('message'))

    def test_template_sms_mobile_number_verification(self):
        mobile = '+1234567890'

        template = self.phantom_env['qcloud.sms.template'].create({
            'name': 'Verification by sms template',
            'domestic_sms_template_ID': '123',
            'domestic_sms_sign': 'Test',
            'international_sms_template_ID': '321',
            'international_sms_sign': 'Test'
        })

        response = self._sms_template_mobile_number_verification(mobile, template.id)
        self.assertEquals(response.get('result'), 0, 'Could not send message')
        res = self._check_verification_code()
        self.assertTrue(res.get('result'), res.get('message'))

    def test_create_and_pay_from_miniprogram_ui(self):
        """
        Create order from mini-program UI, pay, and send the Order to POS
        """
        self.user.write({
            'number_verified': True
        })
        # Pay method ('now' - Pay from mini-program, 'later' - Pay from POS)
        self.create_vals['miniprogram_pay_method'] = 'now'
        order = self._create_from_miniprogram_ui(create_vals=self.create_vals, lines=self.lines)
        self.assertEqual(order.state, 'draft', 'Just created order has wrong state. ')

    def test_create_without_pay_from_miniprogram_ui(self):
        """
        Create order from mini-program UI and send the Order to POS
        """
        self.user.write({
            'number_verified': True
        })
        # Pay method ('now' - Pay from mini-program, 'later' - Pay from POS)
        self.create_vals['miniprogram_pay_method'] = 'later'

        order = self._create_from_miniprogram_ui(create_vals=self.create_vals, lines=self.lines)
        self.assertEqual(order.state, 'draft', 'Just created order has wrong state. ')
