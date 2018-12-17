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
from operator import itemgetter
from odoo import fields, models, api, _


class AllocationType(models.Model):
    """Allocation type from budget line"""
    _name = "budget.allocation.type"

    name = fields.Char('Name', required=True)


class BudgetItem(models.Model):

    """ Budget Item

    This is a link between budgets and financial accounts. """
    _name = "budget.item"
    _description = "Budget items"
    _order = 'sequence ASC, name ASC'

    def _get_all_account_ids(self):
        for item in self:
            if not item.account:
                continue
            account_ids = [account.id for account in item.account]
            item.all_account_ids = self.env['account.account'].browse(account_ids)

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    parent_id = fields.Many2one('budget.item', string='Parent Item', ondelete='cascade')
    children_ids = fields.One2many('budget.item', 'parent_id', string='Children Items')
    account = fields.Many2many('account.account', string='Financial Account')
    note = fields.Text('Notes')
    calculation = fields.Text('Calculation')
    type = fields.Selection([('view', 'View'), ('normal', 'Normal')], string='Type', required=True, default='normal')
    sequence = fields.Integer('Sequence')
    allocation_id = fields.Many2one('budget.allocation.type', string='Budget Line Allocation Type')
    style = fields.Selection([('normal', 'Normal'), ('bold', 'Bold'), ('invisible', 'Invisible')],
                             string='Style', required=True, default='normal')
    all_account_ids = fields.Many2many('account.account', compute=_get_all_account_ids, string='Accounts and Children Accounts')

    def get_sub_item_ids(self, item_ids):
        """ Returns list of ids of sub items (including the top level
        item id)"""
        tree = self.get_flat_tree(item_ids)
        return [item['id'] for item in tree]

    def get_flat_tree(self, root_ids):
        """ return informations about a buget items tree structure.

        Data are returned in a list of dicts with the items values.
        Data are sorted as in the pre-order walk
        algorithm in order to allow to display easily the tree in reports
        """
        def recurse_tree(node_ids, level=0):
            result = []
            items = self.read(node_ids,
                              ['code', 'name', 'sequence',
                               'type', 'style', 'children_ids'],)
            all_children_ids = []
            for item in items:
                children_ids = item.pop('children_ids')
                if children_ids:
                    all_children_ids += children_ids
                item['level'] = level
            result += items
            if all_children_ids:
                result += recurse_tree(all_children_ids, level + 1)
            return result
        if not hasattr(root_ids, '__iter__'):
            root_ids = [root_ids]
        return recurse_tree(root_ids)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """search not only for a matching names but also
        for a matching codes """
        if args is None:
            args = []
        domain = ['|', ('name', operator, name), ('code', operator, name)]
        items = self.search(domain + args, limit=limit)
        return items.name_get()

    # TODO: check it
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """ special search. If we search an item from the budget
        version form (in the budget lines)
        then the choice is reduce to periods
        that overlap the budget dates"""
        domain = []
        if self._context.get('budget_id'):
            ctx = self._context.copy()
            ctx.pop('budget_id')  # avoid recursion for underhand searches
            budget = self.env['budget.budget'].browse(self._context.get('budget_id'))

            allowed_item_ids = self.get_sub_item_ids([budget.budget_item_id.id])
            domain = [('id', 'in', allowed_item_ids)]
        return super(BudgetItem, self).search(args + domain, offset, limit, order, count)
