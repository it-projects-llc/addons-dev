##############################################################################
#
#    Author: Arnaud Wüst
#    Copyright 2009-2013 Camptocamp SA
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
from datetime import datetime
import calendar

from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DTF


class BudgetBudget(models.Model):

    """ Budget Model. The module's main object.  """
    _name = "budget.budget"
    _description = "Budget"
    _order = 'name ASC'

    @api.depends('budget_version_ids', 'budget_version_ids.is_active')
    def _compute_active_version(self):
        if self.budget_version_ids:
            self.active_version_id = self.budget_version_ids.filtered(lambda x: x.is_active is True).id

    code = fields.Char('Code')
    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=lambda *args: 1)
    start_date = fields.Date('Start Date', required=True)
    stop_date = fields.Date('End Date')
    budget_item_id = fields.Many2one('budget.item', 'Budget Structure', required=True, ondelete='restrict')
    budget_version_ids = fields.One2many('budget.version', 'budget_id', 'Budget Versions', readonly=True)
    active_version_id = fields.Many2one('budget.version', compute=_compute_active_version, string='Active Version')
    note = fields.Text('Notes')
    create_date = fields.Datetime('Creation Date', readonly=True)

    @api.onchange('start_date', 'stop_date')
    def _onchange_start_stop_date(self):
        if self.start_date and not self.stop_date:
            start_date = datetime.strptime(self.start_date, DTF)
            last_day_of_month = calendar.monthrange(start_date.year, start_date.month)[1]
            self.stop_date = datetime(year=start_date.year, month=start_date.month, day=last_day_of_month)

        if self.stop_date and not self.start_date:
            self.stop_date = False
            return {
                'warning': {
                    'title': _("Error"),
                    'message': _("Date Error: The end date is defined before the start date"),
                }
            }

        if self.stop_date and self.start_date and self.stop_date < self.start_date:
            return {
                'warning': {
                    'title': _("Error"),
                    'message': _("End Date cannot be earlier then Start Date"),
                }
            }

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ Extend search to look in name and code """
        if args is None:
            args = []
        domain = ['|', ('name', operator, name), ('code', operator, name)]
        budgets = self.search(domain + args, limit=limit)
        return budgets.name_get()
