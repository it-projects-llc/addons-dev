# -*- coding: utf-8 -*-

from openerp import fields, models, api


class MemberType(models.Model):
    _name = 'sale_membership.type'
    _order = 'points'

    name = fields.Char('Membership type')
    points = fields.Integer('Promote at', default=0)


class MemberLog(models.Model):

    _name = 'sale_membership.log'

    partner_id = fields.Many2one('res.partner', string='Partner')
    member_type_id = fields.Many2one('sale_membership.type', string='New Membership Type')
    reason = fields.Char(string='Reason', help='Reason of membership change. But if blocked=True then reason of blocking')
    blocked = fields.Boolean('Blocked', default='False')


class Person(models.Model):

    _inherit = 'res.partner'

    points = fields.Float(string='Current membership Points', default=0)
    type_id = fields.Many2one('sale_membership.type', compute='set_membership', string='Current Membership type', store=True)
    blocked = fields.Boolean(default=False, string='Blocked', readonly=True)

    @api.one
    @api.depends('points', 'customer')
    def set_membership(self):
        if not self.customer:
            return
        smt = self.env['sale_membership.type'].search([])
        smt_last_index = len(smt) - 1
        if not len(smt):
            return
        if self.points >= smt[smt_last_index].points:
            self.type_id = smt[smt_last_index].id
        else:
            for r in range(smt_last_index):
                if self.points >= smt[r].points and self.points < smt[r+1].points:
                    self.type_id = smt[r].id
                    break

