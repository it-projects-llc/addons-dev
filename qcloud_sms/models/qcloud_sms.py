# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from qcloudsms_py.httpclient import HTTPError
    import phonenumbers
    _sms_phonenumbers_lib_imported = True
except ImportError as err:
    _sms_phonenumbers_lib_imported = False
    _logger.debug(err)


class QCloudSMS(models.Model):
    """Records with information about SMS messages."""

    _name = 'qcloud.sms'
    _description = 'SMS Messages'
    _order = 'id desc'

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('done', 'Delivered'),
        ('error', 'Error'),
    ]

    partner_ids = fields.Many2many('res.partner', string='Partner')
    send_datetime = fields.Datetime(string='Sent', readonly=True, help='Date and Time of sending the message',
                                    default=fields.Datetime.now)
    message = fields.Text(string='Message', required=True)
    state = fields.Selection(STATE_SELECTION, string='Status', readonly=True, default='draft',
                             help='Status of the SMS message')
    template_id = fields.Many2one('qcloud.sms.template', 'SMS Template')

    def _phone_get_country(self, partner):
        if 'country_id' in partner:
            return partner.country_id
        return self.env.user.company_id.country_id

    def _sms_sanitization(self, partner):
        number = partner.mobile
        if number and _sms_phonenumbers_lib_imported:
            country = self._phone_get_country(partner)
            country_code = country.code if country else None
            try:
                phone_nbr = phonenumbers.parse(number, region=country_code, keep_raw_input=True)
            except phonenumbers.phonenumberutil.NumberParseException as e:
                raise UserError(_('Unable to parse %s:\n%s') % (number, e))

            if not phonenumbers.is_possible_number(phone_nbr) or not phonenumbers.is_valid_number(phone_nbr):
                raise UserError(_('Invalid number %s: probably incorrect prefix') % number)
            return phone_nbr
        else:
            raise UserError(_("The `phonenumbers` Python module is not available."
                              "Try `pip3 install phonenumbers` to install it."))

    @api.model
    def send_message(self, message, partner_id, **kwargs):
        try:
            result = self._send_message(message, partner_id, **kwargs)
        except HTTPError as e:
            return {
                'error': _('Error on sending SMS: %s') % e.response.text
            }
        _logger.debug('Send message JSON result: %s', result)
        return result

    @api.model
    def _send_message(self, message, partner_id, **kwargs):
        """Send Message

        :param message: SMS message
        :param partner_id: id of partner
        """
        partner = self.env['res.partner'].browse(partner_id)
        vals = {
            'message': message,
            'partner_ids': partner,
            'template_id': kwargs.get('template_id') or None,
        }

        # create new record
        sms = self.create(vals)

        # get SMS object
        qcloudsms = self.env['ir.config_parameter'].get_qcloud_sms_object()
        ssender = qcloudsms.SmsSingleSender()

        try:
            phone_obj = self._sms_sanitization(partner)
        except UserError as e:
            sms.state = 'error'
            _logger.debug(e)
            raise

        country_code = phone_obj.country_code
        national_number = phone_obj.national_number
        sms_type = sms.template_id.sms_type if sms.template_id else 0

        _logger.debug("Country code: %s, Mobile number: %s", country_code, national_number)

        # China Country Code 86 (use domestics templates)
        if country_code == '86':
            template_ID = sms.template_id.domestic_sms_template_ID if sms.template_id else False
            params = sms.template_id.domestic_template_params if sms.template_id else False
            sign = sms.template_id.domestic_sms_sign if sms.template_id else False
        else:
            template_ID = sms.template_id.international_sms_template_ID if sms.template_id else False
            params = sms.template_id.international_template_params if sms.template_id else False
            sign = sms.template_id.international_sms_sign if sms.template_id else False

        params = params.split(',')

        extend_field = kwargs.get('extend_field') or ""

        if template_ID or sign:
            result = ssender.send_with_param(country_code, national_number, template_ID,
                                             params, sign=sign, extend=extend_field, ext=sms.id)
        else:
            result = ssender.send(sms_type, country_code, national_number,
                                  message, extend=extend_field, ext=sms.id)

        if result.get('result') == 0:
            sms.state = 'sent'
        else:
            sms.state = 'error'

        return result

    @api.model
    def send_group_message(self, message, partner_ids, **kwargs):
        try:
            result = self._send_group_message(message, partner_ids, **kwargs)
        except HTTPError as e:
            return {
                'error': _('Error on sending SMS: %s') % e.response.text
            }
        _logger.debug('Send message JSON result: %s', result)
        return result

    @api.model
    def _send_group_message(self, message, partner_ids, **kwargs):
        """Send a message to a group of partners

        :param message: SMS message
        :param partner_ids: list of partners ids
        """
        partners = self.env['res.partner'].browse(partner_ids)

        vals = {
            'message': message,
            'partner_ids': partners,
            'template_id': kwargs.get('template_id') or None,
        }

        # create new record
        sms = self.create(vals)

        # get SMS object
        qcloudsms = self.env['ir.config_parameter'].get_qcloud_sms_object()
        msender = qcloudsms.SmsMultiSender()

        try:
            phone_obj_list = map(self._sms_sanitization, partners)
        except UserError as e:
            sms.state = 'error'
            _logger.debug(e)

        country_code_list = list(map(lambda x: x.country_code, phone_obj_list))
        country_code = list(set(country_code_list))

        if len(country_code) > 1:
            raise UserError(_('The country code must be the same for all phone numbers'))

        country_code = country_code[0]
        national_number_list = list(map(lambda x: x.national_number, phone_obj_list))

        _logger.debug("Country code: %s, Mobile numbers: %s", country_code, national_number_list)

        sms_type = sms.template_id.sms_type if sms.template_id else 0

        # China Country Code 86 (use domestics templates)
        if country_code == '86':
            template_ID = sms.template_id.domestic_sms_template_ID if sms.template_id else False
            params = sms.template_id.domestic_template_params if sms.template_id else False
            sign = sms.template_id.domestic_sms_sign if sms.template_id else False
        else:
            template_ID = sms.template_id.international_sms_template_ID if sms.template_id else False
            params = sms.template_id.international_template_params if sms.template_id else False
            sign = sms.template_id.international_sms_sign if sms.template_id else False

        params = params.split(',')

        extend_field = kwargs.get('extend_field') or ""

        if template_ID or sign:
            # send sms by params
            result = msender.send_with_param(country_code, national_number_list, template_ID, params, sign=sign,
                                             extend=extend_field, ext=sms.id)
        else:
            result = msender.send(sms_type, country_code, national_number_list,
                                  message, extend=extend_field, ext=sms.id)

        if result.get('result') == 0:
            sms.state = 'sent'
        else:
            sms.state = 'error'

        return result


class QCloudSMSTemplate(models.Model):
    """Templates of SMS messages."""

    _name = 'qcloud.sms.template'
    _description = 'SMS Templates'
    _order = 'id desc'

    name = fields.Char(string='Name', help='The template name')

    domestic_sms_template_ID = fields.Integer(
        string='Domestic SMS Template ID',
        help='SMS Template ID is the Tencent Cloud SMS template (the specific content of the SMS message to be sent).'
    )
    domestic_template_params = fields.Text(
        string="Domestic Template parameters",
        help="Parameters must be separated by commas. If the template has no parameters, leave it empty."
    )
    domestic_sms_sign = fields.Char(
        string='Domestic SMS Signature',
        help='SMS Signature is the Tencent Cloud SMS signature (an identifier added before the message body for '
             'identification of the company or business.).'
    )
    international_sms_template_ID = fields.Integer(
        string='International SMS Template ID',
        help='SMS Template ID is the Tencent Cloud SMS template (the specific content of the SMS message to be sent).'
    )
    international_template_params = fields.Text(
        string="International Template parameters",
        help="Parameters must be separated by commas. If the template has no parameters, leave it empty."
    )
    international_sms_sign = fields.Char(
        string='International SMS Signature ID',
        help='SMS Signature is the Tencent Cloud SMS signature (an identifier added before the message body for '
             'identification of the company or business.).'
    )
    sms_type = fields.Selection([
        (0, 'Normal'),
        (1, 'Marketing')
    ], string='SMS Type', default='normal', help='Type of SMS message')
