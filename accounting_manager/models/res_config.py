# -*- coding: utf-8 -*-
from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.multi
    def execute(self):
        if self.env['res.users'].has_group('accounting_manager.group_fact_manager') and \
           self._name == 'account.config.settings':
            self = self.sudo()

        return super(ResConfigSettings, self).execute()
