# -*- coding: utf-8 -*-

from openerp import fields, models, api


class MemberType(models.Model):
    _name = 'sale_membership.type'
    _order = 'sequence'

    name = fields.Char('Membership type')
    points = fields.Integer('Promote at', default=0)
    sequence = fields.Integer(help='Membership order')


class MemberLog(models.Model):

    _name = 'sale_membership.log'

    name = fields.Char(string='Name')
    partner_id = fields.Many2one('res.partner', string='Partner')
    member_type_id = fields.Many2one('sale_membership.type')
    log_record_date = fields.Datetime(string='Date of change', required=True, readonly=True,
                                  default=fields.Date.context_today, timestamp=True)
    reason = fields.Char(string='Reason')
    blocked = fields.Boolean('Blocked', default='False')


class Person(models.Model):

    _inherit = 'res.partner'

    points = fields.Integer(string='Points', default=0, readonly=True)
    log_id = fields.Many2one('sale_membership.log', compute='get_membership', string='Membership type', store=True)

    @api.one
    @api.depends('points')
    def get_membership(self):
        query = """SELECT id
                   FROM sale_membership_log
                   WHERE partner_id = %s
                   ORDER BY log_record_date DESC
                   LIMIT 1""" % (self.id)
        self.env.cr.execute(query)
        query_results = self.env.cr.dictfetchall()
        self.log_id = query_results[0]
        # Exceptions ?




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
