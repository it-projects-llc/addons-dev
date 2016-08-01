# -*- coding: utf-8 -*-
from openerp import models, fields, api
import re
from openerp.exceptions import UserError
from datetime import date


class PersonalIdentificationType(models.Model):
    _name = 'personal.identification_type'

    name = fields.Char(string='Identification Type', required=True)

    regexp_force = fields.Char(string='Regexp Force', default='.*')
    error_message = fields.Char(string='Error message')


class PersonalDriveLicenseType(models.Model):
    _name = 'personal.drive_license_type'

    name = fields.Char(string='License Type', required=True)

    regexp_force = fields.Char(string='Regexp Force', default='.*')
    error_message = fields.Char(string='Error message')


class PersonalEmergencyContact(models.Model):
    _name = 'personal.emergency_contact'

    name = fields.Char(string='Name')
    relation = fields.Char(string='Relation')
    phone = fields.Char(string='Phone number')
    mobile = fields.Char(string='Mobile number')
    partner_id = fields.Many2one('res.partner')


class Person(models.Model):
    _inherit = 'res.partner'

    nationality_id = fields.Many2one('res.country', string='Nationality')
    birthdate_date = fields.Date(string='Birthdate')
    age = fields.Integer(compute='_get_age', type='integer', string='Age')

    identification_type_id = fields.Many2one('personal.identification_type', string='Identification Type')
    identification_number = fields.Char('Identification Number')
    issuer = fields.Char(string='Issuer string')
    issuer_date = fields.Date(string='Date of Issue')

    license_type_id = fields.Many2one('personal.drive_license_type', string='Drive License Type')
    license_number = fields.Char(string='Drive License Number')
    license_expiry_date = fields.Date(string='Drive License Expiry Date')

    firstname = fields.Char(string='First Name')
    secondname = fields.Char(string='Second Name')
    thirdname = fields.Char(string='Third Name')
    familyname = fields.Char(string='Family Name')

    work_phone = fields.Char(string='Work Phone')

    emergency_contact_ids = fields.One2many('personal.emergency_contact', 'partner_id')

    @api.one
    @api.onchange('firstname', 'secondname')
    @api.constrains('firstname', 'secondname')
    def build_name(self):
        if self.secondname and self.firstname:
            self.name = '%s %s' % (self.secondname or '', self.firstname or '')

    @api.one
    @api.onchange('identification_number', 'license_type_id')
    def fill_license_number(self):
        if self.license_type_id.name in ['Private', 'General']:
            self.license_number = self.identification_number

    @api.one
    @api.depends('birthdate_date')
    def _get_age(self):
        today = date.today()
        age = False
        if self.birthdate_date:
            birthdate = fields.Date.from_string(self.birthdate_date)
            try:
                birthday = birthdate.replace(year=today.year)
            # raised when birth date is February 29 and the current year is
            # not a leap year
            except ValueError:
                birthday = birthdate.replace(
                    year=today.year, day=birthdate.day - 1)
            if birthday > today:
                age = today.year - birthdate.year - 1
            else:
                age = today.year - birthdate.year
        self.age = age

    @api.one
    @api.constrains('birthdate_date')
    def _check_age(self):
        if self.customer and self.birthdate_date and self.age < 21:
            raise UserError('Age restriction. Person must be elder than 21.')

    @api.one
    @api.constrains('identification_number')
    def _check_identification_number(self):
        if not re.match(self.identification_type_id.regexp_force, self.identification_number):
            raise UserError(self.identification_type_id.error_message)
