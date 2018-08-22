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

        self.Order = self.phantom_env['wechat.order']
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
        floor = self.phantom_env.ref('pos_restaurant.floor_main')
        table = self.phantom_env.ref('pos_restaurant.table_01')

        self.create_vals = {
            'note': 'This is test Order note',
            'floor_id': floor.id,
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

    def _mobile_number_verification(self, mobile):
        response_json = {
            "result": 0,
            "errmsg": "OK",
            "ext": "",
            "fee": 1,
            "sid": "xxxxxxx"
        }
        patch_url = 'qcloudsms_py.util.api_request'
        self._patch_post_requests(response_json, patch_url)

        return self.user.mobile_number_verification(mobile)

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

        return self.phantom_env['wechat.order'].create_from_miniprogram_ui(lines, create_vals)

    def test_mobile_number_verification(self):
        mobile = '+1234567890'
        response = self._mobile_number_verification(mobile)
        self.assertEquals(response.get('result'), 0, 'Could not send message')
        result = self._check_verification_code()
        self.assertTrue(result, "Verification code does not match")

    def test_create_and_pay_from_miniprogram_ui(self):
        """
        Create order from mini-program UI, pay, and send the Order to POS
        """
        # pay method (Pay Now - 0, Pay Later - 1)
        self.create_vals['miniprogram_pay_method'] = 0
        res = self._create_from_miniprogram_ui(create_vals=self.create_vals, lines=self.lines)
        order_id = res.get('order_id')
        order = self.Order.browse(order_id)

        self.assertEqual(order.state, 'draft', 'Just created order has wrong state. ')

        # simulate notification
        notification = {
            'return_code': 'SUCCESS',
            'result_code': 'SUCCESS',
            'out_trade_no': order.name,
        }

        handled = self.Order.on_notification(notification)

        self.assertTrue(handled, 'Notification was not handled (error in checking for duplicates?) ')
        self.assertEqual(order.state, 'done', "Order's state is not changed after notification about update. ")

    def test_create_without_pay_from_miniprogram_ui(self):
        """
        Create order from mini-program UI and send the Order to POS
        """
        # pay method (Pay Now - 0, Pay Later - 1)
        self.create_vals['miniprogram_pay_method'] = 1

        res = self._create_from_miniprogram_ui(create_vals=self.create_vals, lines=self.lines)
        self.assertTrue(res, 'Cannot send the order to POS')
