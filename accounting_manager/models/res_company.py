# -*- coding: utf-8 -*-

from collections import defaultdict, MutableMapping, OrderedDict
from odoo import api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    country_id = fields.Many2one(required=True)

    @api.onchange('state_id')
    def _onchange_state(self):
        # this onchange method is the same as in the base module but with one exception - the if statement,
        # without it country field has not got its default value from ir.values default
        if self.state_id:
            self.country_id = self.state_id.country_id

    @api.model
    def create(self, vals):
        company = super(Company, self).create(vals)
        fact_managers = self.env['res.users'].search([('groups_id', 'in', [self.env.ref('accounting_manager.group_fact_manager').id])])
        if fact_managers:
            fact_managers.write({'company_ids': [(4, company.id, 0)]})
        return company
