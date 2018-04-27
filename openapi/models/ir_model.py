# -*- coding: utf-8 -*-
# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class IrModel(models.Model):
    _inherit = 'ir.model'

    api_access_ids = fields.One2many('openapi.access', 'model_id', 'Access via API')
