# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import ValidationError, Warning, except_orm


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_serviceman = fields.Boolean(
        string='Serviceman',
        help='if checked the partner is a serviceman.')
    is_operator = fields.Boolean(
        string='Operator',
        help='if checked the partner is an operator.')
    is_manager = fields.Boolean(
        string='Manager',
        help='if checked the partner is a manager.')
    partner_user_id = fields.Many2one('res.users', string='Customer user id')

    @api.multi
    def create_user(self, password=False):
        """Create user from Customer."""
        # Raise warning if the email is not entered in the new record.
        if not self.email:
            raise ValidationError('Please Enter Email!')
        # Creating the vals dictionary for a new user.
        user_vals = {
            'name': self.name,
            'login': self.email,
            'partner_id': self.id,
            'password': password or self.company_id.default_password
        }
        if self.customer:
            user_vals.update({
                'customer': True,
                'groups_id': [(6, 0, [self.env.ref('field_service_management.group_customer').id])],
            })
        # Creating User Record.
        user_rec = self.env['res.users'].create(user_vals)
        # Set the Customer user in Partner
        self.partner_user_id = user_rec.id
        return user_rec

    @api.multi
    def open_user(self):
        """
        This Method is used to Open User from customer record.
        @param self: The object pointer
        """
        # Created res users open
        context = dict(self._context or {})
        return {
            'view_type': 'form',
            'view_id': self.env.ref('base.view_users_form').id,
            'view_mode': 'form',
            'res_model': 'res.users',
            'res_id': self.partner_user_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
        }
