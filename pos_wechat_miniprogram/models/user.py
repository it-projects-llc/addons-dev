# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models, _
import random
import logging

_logger = logging.getLogger(__name__)

try:
    import phonenumbers
except ImportError as err:
    _logger.debug(err)


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def mobile_number_verification(self, number, **kwargs):
        return self.env.user.partner_id._mobile_number_verification(number, **kwargs)

    @api.model
    def wechat_mobile_number_verification(self, data):
        return self.env.user.partner_id._wechat_mobile_number_verification(data)

    @api.model
    def check_verification_code(self, code):
        return self.env.user.partner_id._check_verification_code(code)


class ResPartner(models.Model):
    _inherit = "res.partner"

    number_verified = fields.Boolean(string='Verified', default=False)
    verification_code = fields.Char(string='Verification code')

    @api.multi
    def _mobile_number_verification(self, number, **kwargs):
        """
        Send verification code to mobile number

        :param number: mobile number from mini-program
        :return result: result of send
        """
        self.ensure_one()
        Qcloud = self.env['qcloud.sms']
        code = random.randrange(10000, 1000000)

        country = Qcloud._get_country(self)
        country_code = country.code if country else None

        phone_obj = phonenumbers.parse(number, region=country_code, keep_raw_input=True)
        phone_number = phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        self.write({
            'mobile': phone_number,
        })

        message = _("Your login verification code is %s. If you are not using our service, "
                    "ignore the message.") % (code)

        result = Qcloud.send_message(message, self.id, **kwargs)

        sms = self.env['qcloud.sms'].browse(result.get('sms_id'))

        if sms.state == 'sent':
            self.write({
                'verification_code': code,
            })

        return result

    @api.multi
    def _wechat_mobile_number_verification(self, data):
        """
        Save WeChat mobile number

        :param data: data['encryptedData'] Encrypted data with complete user information including sensitive data
        :param data: data['iv'] Initial vector of the encryption algorithm
        :return result: result of wechat phone number verification
        """
        self.ensure_one()

        encryptedData = data.get('encryptedData')
        iv = data.get('iv')
        session_key = self.wechat_session_key
        res = self.env['ir.config_parameter'].sudo().decrypt_wechat_miniprogram_data(session_key, encryptedData, iv)
        PhoneNumber = res.get('phoneNumber')
        phone_obj = phonenumbers.parse(PhoneNumber, keep_raw_input=True)
        phone_number = phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        self.write({
            'mobile': phone_number,
            'number_verified': True
        })

        return {'result': True}

    @api.multi
    def _check_verification_code(self, code):
        """
        :param code: verification code from a sms
        :return result: verification result
        """
        self.ensure_one()
        if self.verification_code == code:
            self.write({
                'number_verified': True
            })
            return {'result': True}
        else:
            return {'result': False}
