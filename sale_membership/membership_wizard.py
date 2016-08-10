# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import UserError


class MembershipWizard(models.TransientModel):
    _name = 'sale_membership.membership_wizard'

    partner_id = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)], required=True)
    membership_type_id = fields.Many2one('sale_membership.type', related='partner_id.type_id', string='Membership')
    new_membership_type_id = fields.Many2one('sale_membership.type', string='Choose new membership')

    action_type = fields.Selection([
            ('block','Block'),
            ('demote','Demote'),
        ])

    demoting_reason = fields.Text(string='Demoting reason')
    blocking_reason = fields.Text(string='Blocking reason')

    @api.one
    @api.constrains('new_membership_type_id')
    def _check_new_membership_type(self):
        if self.action_type == 'demote':
            if self.membership_type_id.points == 0:
                raise UserError('You cannot demote %s membership type' % self.membership_type_id.name)
            if self.new_membership_type_id:
                if self.new_membership_type_id.points >= self.membership_type_id.points:
                    raise UserError('Select new membership type that is less than current')
            else:
                raise UserError('Select new membership type for demote')

    @api.multi
    def apply_membership(self):
        if self.new_membership_type_id:
            self.partner_id.write({'demoting_offset': self.partner_id.points - self.new_membership_type_id.points})
            self.env['sale_membership.log'].create({'partner_id': self.partner_id.id,
                                                    'member_type_id': self.new_membership_type_id.id,
                                                    'reason': self.demoting_reason,
                                                    })
        elif self.action_type == 'block':
            self.partner_id.write({'blocked': True})
            self.env['sale_membership.log'].create({'partner_id': self.partner_id.id,
                                                    'blocked': True,
                                                    'reason': self.blocking_reason,
                                                    })



