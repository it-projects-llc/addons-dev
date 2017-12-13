# -*- coding: utf-8 -*-
from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.multi
    def execute(self):
        if self.env['res.users'].has_group('accounting_manager.group_fact_manager'):
            self = self.sudo()

        return super(ResConfigSettings, self).execute()

    @api.model
    def get_values(self):
        if self.env['res.users'].has_group('accounting_manager.group_fact_manager'):
            self = self.sudo()
        res = super(ResConfigSettings, self).get_values()
        return res
