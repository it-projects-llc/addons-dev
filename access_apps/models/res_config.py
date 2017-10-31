# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _install_modules(self, modules):
        if self.env['res.users'].has_group('access_apps.group_allow_apps_only_from_settings'):
            result = super(ResConfigSettings, self.sudo())._install_modules(modules)
        else:
            result = super(ResConfigSettings, self)._install_modules(modules)

        return result
