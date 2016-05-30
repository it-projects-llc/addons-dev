# -*- coding: utf-8 -*-
# fb - fleet booking

from openerp import fields, models

class MemberType(models.Model):
    _name = 'fb.member_type'
    _order = 'sequence'

    name = fields.Char('Membership type')
    points = fields.Integer('Promote at', default=0)
    sequence = fields.Integer(help='Membership order')


class MemberLog(models.Model):

    _name = 'fb.member_log'

    member_type = fields.Many2one('fleet_booking.member_type')
    date = fields.Date(string='Date of change', required=True, readonly=True,
                       default=fields.Date.context_today, timestamp=True)
    reason = fields.Selection([(u'Promote', u'Promote'),
                               (u'Demote', u'Demote'),
                               (u'Other', u'Other')],
                              string='Reason')

class Person(models.Model):

    _inherit = 'res.partner'

    points = fields.Integer(string='Points')
    membership_id = fields.Many2one('fb.member_log', compute='get_membership', string='Membership')

    def get_membership(self):
        query = """SELECT MAX(a.date)
                   FROM fb_member_log as a
                   WHERE a.id = %s""" % (self.id)
        self.env.cr.execute(query)
        query_results = self.env.cr.dictfetchall()
        return query_results
