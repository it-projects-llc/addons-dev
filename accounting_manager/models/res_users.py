# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.addons.base.res.res_users import name_boolean_group, parse_m2m


class User(models.Model):

    _inherit = ['res.users']

    @api.multi
    def write(self, vals):
        result = super(User, self).write(vals)
        group_fact_manager = self.env.ref('accounting_manager.group_fact_manager')
        if vals.get('groups_id') and group_fact_manager.id in parse_m2m(vals['groups_id']) or \
           vals.get(name_boolean_group(group_fact_manager.id)):
            self.write({'company_ids': [(6, 0, self.env['res.company'].search([]).ids)]})
        return result

    @api.model
    def create(self, values):
        user = super(User, self).create(values)
        if user.has_group('accounting_manager.group_fact_manager'):
            user.write({'company_ids': [(6, 0, self.env['res.company'].search([]).ids)]})
        return user


class Groups(models.Model):

    _inherit = "res.groups"

    @api.multi
    def write(self, vals):
        result = super(Groups, self).write(vals)
        group_fact_manager = self.env.ref('accounting_manager.group_fact_manager')

        if group_fact_manager.id in self.ids and vals.get('users'):
            users = self.env['res.users'].browse(parse_m2m(vals['users']))
            users.write({'company_ids': [(6, 0, self.env['res.company'].search([]).ids)]})

        return result
