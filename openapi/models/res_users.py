# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    namespace_ids = fields.Many2many('openapi.namespace', string='Allowed Integrations')
