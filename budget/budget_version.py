##############################################################################
#
#    Author: Arnaud Wüst, Leonardo Pistone
#    Copyright 2009-2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import fields, api, models


class BudgetVersion(models.Model):

    """ Budget version.

    A budget version is a budget made at a given time for a given company.
    It also can have its own currency """

    _name = "budget.version"
    _description = "Budget versions"
    _order = 'name ASC'

    code = fields.Char('Code')
    name = fields.Char('Version Name', required=True)
    budget_id = fields.Many2one('budget.budget', string='Budget', required=True, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get('account.account'))
    user_id = fields.Many2one('res.users', string='User In Charge')
    budget_line_ids = fields.One2many('budget.line', 'budget_version_id', string='Budget Lines')
    note = fields.Text('Notes')
    create_date = fields.Datetime('Creation Date', readonly=True)
    ref_date = fields.Date('Reference Date', required=True, default=fields.Date.context_today)
    is_active = fields.Boolean('Active version', readonly=True,
                               help='Each budget can have no more than one active version.')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Extend search to name and code. """
        if args is None:
            args = []
        domain = ['|', ('name', operator, name), ('code', operator, name)]
        versions = self.search(domain + args, limit=limit)
        return versions.name_get()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        self.write({
            'is_active': False
        })
        if default is None:
            default = {}
        default['budget_line_ids'] = []
        return super(BudgetVersion, self).copy(default)

    @api.multi
    def make_active(self):
        for r in self:
            r.write({'is_active': True})
            other_versions = self.search([('budget_id', '=', r.budget_id.id), ('id', '!=', r.id)])
            other_versions.write({'is_active': False})
