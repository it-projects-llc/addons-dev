# -*- coding: utf-8 -*-

from openerp import api, fields, models


class HrDepartment(models.Model):

    _name = "fleet_booking.branch"
    _inherit = 'hr.department'

    city = fields.Char(string='City')
    phone = fields.Char(string='Phone')
    branch_target = fields.Char(string='Branch Target')


class Person(models.Model):

    _inherit = 'res.partner'

    id_type = fields.Selection(
        [(u'National Id', u'National Id'), (u'Iqama', u'Iqama'),
         (u'Passport', u'Passport')],
        string='ID Type',
        )
    issuer = fields.Char(string='Issuer string')
    issuer_date = fields.Date(string='Date of Issue')
    license_type = fields.Selection([(u'Private', u'Private'),
                                     (u'General', u'General'),
                                     (u'International', u'International')],
                                    string='License Type')
    license_number = fields.Char(string='License Number')
    third_name = fields.Char(string='Third Name')
    family_name = fields.Char(string='Family Name')

    def check_age(self, cr, uid, ids, context=None, parent=None):
        for r in self.browse(cr, uid, ids, context=context):
            if r.customer and r.birthdate_date and r.age < 21:
                return False
        return True

    _constraints = [
        (check_age, 'Age restriction. Person must be elder than 20.', ['birthdate_date']),
    ]


class Membership(models.Model):

    _name = 'membership'

    partner = fields.Many2one('res.partner')
    member_type = fields.Selection([(u'Bronze', u'Bronze'),
                                    (u'Silver', u'Silver'),
                                    (u'Gold', u'Gold')],
                                   string='Membership')
    date = fields.Date(string='Date of change')
    reason = fields.Selection([(u'Manual up', u'Manual up'),
                               (u'Manual down', u'Manual down'),
                               (u'Points up', u'Points up'),
                               (u'Points down', u'Points down'),
                               (u'Demote', u'Demote'),
                               (u'Other', u'Other')],
                              string='Membership')

    def check_age(self, cr, uid, ids, context=None, parent=None):
        for r in self.browse(cr, uid, ids, context=context):
            if r.customer and r.birthdate_date and r.age < 21:
                return False
        return True

    _constraints = [
        (check_age, 'Age restriction. Person must be elder than 20.', ['birthdate_date']),
    ]
