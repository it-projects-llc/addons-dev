# -*- coding: utf-8 -*-
import re
from openerp import models, fields, api
from openerp.exceptions import UserError


class PersonalDriveLicenseType(models.Model):
    _name = 'personal.drive_license_type'

    name = fields.Char(string='License Type', required=True)

    regexp_force = fields.Char(string='Regexp Force', default='.*')
    error_message = fields.Char(string='Error message')


class PersonalDriveLicense(models.AbstractModel):
    _name = 'personal.drive_license'

    license_type_id = fields.Many2one('personal.drive_license_type', string='License Type')
    license_number = fields.Char(string='License Number')
    issuer = fields.Char(string='Issuer')
    license_expiry_date = fields.Date(string='License Expiry Date')

    @api.one
    @api.constrains('license_number')
    def _check_license_number(self):
        if not re.match(self.license_type_id.regexp_force, self.license_number):
            raise UserError(self.license_type_id.error_message)

