# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging
import werkzeug.urls
import base64
import json

from odoo import models, api, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)

try:
    from Crypto.Cipher import AES
    from wechatpy import WeChatPay
except ImportError as err:
    _logger.debug(err)


class Param(models.Model):

    _inherit = 'ir.config_parameter'

    @api.model
    def get_wechat_miniprogram_pay_object(self):
        sandbox = self.sudo().get_param('wechat.sandbox', '0') != '0'
        if sandbox:
            _logger.info('Sandbox Mode is used for WeChat API')
        _logger.debug('WeChat Credentials: miniprogram_app_id=%s, miniprogram_app_secret=%s, mch_id=%s, sub_mch_id=%s, sandbox mode is %s',
                      self.sudo().get_param('wechat.miniprogram_app_id', ''),
                      '%s...' % self.sudo().get_param('wechat.miniprogram_app_secret', '')[:5],
                      self.sudo().get_param('wechat.mch_id', ''),
                      self.sudo().get_param('wechat.sub_mch_id', ''),
                      sandbox
                      )
        return WeChatPay(
            self.sudo().get_param('wechat.app_id', ''),
            self.sudo().get_param('wechat.app_secret', ''),
            self.sudo().get_param('wechat.mch_id', ''),
            sub_mch_id=self.sudo().get_param('wechat.sub_mch_id', ''),
            sandbox=sandbox,
            sub_appid=self.sudo().get_param('wechat.miniprogram_app_id', '')
        )

    def get_openid_url(self, code):
        base_url = 'https://api.weixin.qq.com/sns/jscode2session'
        param = {
            'appid': self.sudo().get_param('wechat.miniprogram_app_id', ''),
            'secret': self.sudo().get_param('wechat.miniprogram_app_secret', ''),
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        url = '%s?%s' % (base_url, werkzeug.urls.url_encode(param))
        _logger.debug('openid url: %s', url)
        return url

    def decrypt_wechat_miniprogram_data(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.env.user.wechat_session_key)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)
        decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)))

        _logger.debug('Decrypt result: %s', decrypted)

        if decrypted['watermark']['appid'] != self.sudo().get_param('wechat.miniprogram_app_id', ''):
            raise UserError(_('Invalid Buffer'))

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]
