# -*- coding: utf-8 -*-
# fb - fleet booking

from openerp import fields, models, api

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
    membership_id = fields.Many2one('fb.member_type', compute='get_membership', string='Membership')

    @api.one
    # @api.depends('name', 'street', 'website')
    def get_membership(self):
        # query = """SELECT member_type
        #            FROM fb_member_log
        #            WHERE id = %s
        #            ORDER BY date DESC
        #            LIMIT 1""" % ('1')
        #            # LIMIT 1""" % (self.id)
        # self.env.cr.execute(query)
        # query_results = self.env.cr.dictfetchall()
        self.membership_id = self.env.ref('loyalty_members.fb_bronze').id




def dump(obj):
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))

def dumpclean(obj):
    if type(obj) == dict:
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print k
                dumpclean(v)
            else:
                print '%s : %s' % (k, v)
    elif type(obj) == list:
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print v
    else:
        print obj
