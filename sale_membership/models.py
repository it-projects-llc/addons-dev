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
    member_type_id = fields.Many2one('sale_membership.type', string='New Membership Type',
                                     ondelete="restrict")
    reason = fields.Text(string='Reason',
                         help='Reason of membership change, if blocked=True then blocking reason')
    blocked = fields.Boolean('Blocked', default=False)


class Person(models.Model):

    _inherit = 'res.partner'

    points = fields.Float(string='Current membership Points', default=0, readonly=True)
    demoting_offset = fields.Integer(help='demoting points', default=0, readonly=True)
    type_id = fields.Many2one('sale_membership.type', compute='set_membership',
                              string='Current Membership type', store=True, readonly=True,
                              ondelete="restrict")
    blocked = fields.Boolean(default=False, string='Blocked', readonly=True)

    @api.one
    @api.depends('points', 'demoting_offset', 'customer')
    def set_membership(self):
        if not self.customer:
            return
        l1 = self.env['sale_membership.type'].search([]).mapped('points')
        real_points = self.points - self.demoting_offset
        l2 = [x for x in l1 if real_points >= x]
        if l2:
            self.type_id = self.env['sale_membership.type'].search([('points', '=', max(l2))]).id
