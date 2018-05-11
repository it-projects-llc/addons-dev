# -*- coding: utf-8 -*-
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# import logging
# from odoo import api
from odoo import fields
from odoo import models
#
# _logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    phonetic_name = fields.Char('Customer Phonetic Name', default="default")
