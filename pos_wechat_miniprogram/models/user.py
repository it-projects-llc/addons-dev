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
        return self.partner_id._mobile_number_verification(number, **kwargs)

    @api.model
    def check_verification_code(self, code):
        return self.partner_id._check_verification_code(code)


class ResPartner(models.Model):
    _inherit = "res.partner"

    number_verified = fields.Boolean(string='Verified', default=False)
    verification_code = fields.Char(string='Verification code')

    @api.model
    def _mobile_number_verification(self, number, **kwargs):

        Qcloud = self.env['qcloud.sms']
        code = random.randrange(10000, 1000000)

        country = Qcloud._phone_get_country(self)
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

    @api.model
    def _check_verification_code(self, code):
        if self.verification_code == code:
            self.write({
                'number_verified': True
            })
            return {'result': True}
        else:
            return {'result': False}
