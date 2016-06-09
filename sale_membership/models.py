# -*- coding: utf-8 -*-

from openerp import fields, models, api


class MemberType(models.Model):
    _name = 'sale_membership.type'
    _order = 'points'

    name = fields.Char('Membership type')
    points = fields.Integer('Promote at', default=0)


class MemberLog(models.Model):

    _name = 'sale_membership.log'

    name = fields.Char(string='Name')
    partner_id = fields.Many2one('res.partner', string='Partner')
    member_type_id = fields.Many2one('sale_membership.type')
    log_record_date = fields.Datetime(string='Date of change', required=True, readonly=True,
                                      default=fields.Date.context_today, timestamp=True)
    reason = fields.Char(string='Reason')
    points = fields.Integer(string='Points', default=0)
    blocked = fields.Boolean('Blocked', default='False')


class Person(models.Model):

    _inherit = 'res.partner'

    points = fields.Integer(string='Points', default=0)
    type_id = fields.Many2one('sale_membership.type', compute='set_membership', string='Membership type', store=True)
    blocked = fields.Boolean(default=False, string='Blocked', readonly=True)

    @api.model
    def default_get(self, fields_list):
        defaults = super(Person, self).default_get(fields_list)
        type_id = self.get_membership()
        if 'type_id' in fields_list:
            defaults.setdefault('type_id', type_id)
        return defaults

    @api.one
    @api.depends('points')
    def set_membership(self):
        smt = self.env['sale_membership.type'].search([('name', '!=', '')])
        smt_last_index = len(smt) - 1
        if smt_last_index < 0:
            self.type_id = None
            return
        if self.points >= smt[smt_last_index].points:
            self.type_id = smt[smt_last_index].id
        else:
            for r in range(smt_last_index):
                if self.points >= smt[r].points and self.points < smt[r+1].points:
                    self.type_id = smt[r].id
                    break
        # vals = {'partner_id': self.id,
        #         'member_type_id': self.type_id.id,
        #         'log_record_date': fields.Datetime.now(),
        #         'reason': 'Automatic',
        #         'name': self.type_id.name,
        #         'points': self.points,
        #         }
        # log_rec = self.env['sale_membership.log'].create(vals)

    def get_membership(self, partner_id=None):
        query_results = []
        if partner_id:
            query = """SELECT id
                       FROM sale_membership_log
                       WHERE partner_id = %s
                       ORDER BY log_record_date DESC
                       LIMIT 1""" % (partner_id)
            self.env.cr.execute(query)
            query_results = self.env.cr.dictfetchall()
        if len(query_results):
            type_id = query_results[0].member_type_id
        else:
            query = """SELECT id
                       FROM sale_membership_type
                       ORDER BY sequence ASC
                       LIMIT 1"""
            self.env.cr.execute(query)
            query_results = self.env.cr.dictfetchall()
            if len(query_results):
                type_id = query_results[0]['id']
            else:
                type_id = None
        return type_id
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
