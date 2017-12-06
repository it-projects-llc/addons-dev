# -*- coding: utf-8 -*-

from odoo import api, models, fields


class User(models.Model):

    _inherit = ['res.users']

    @api.model
    def _update_allowed_companies(self):
        company_id = self.env.context['active_id']
        fact_managers = self.search([('groups_id', 'in', [self.env.ref('accounting_manager.group_fact_manager').id])])
        if fact_managers:
            fact_managers.write({'company_ids': [(4, company_id, 0)]})

    @api.model
    def _on_new_fact_manager(self):
        pass
