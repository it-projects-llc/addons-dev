# coding: utf-8
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class Partner(models.Model):
    _inherit = "res.partner"

    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], default='male', string="Gender")
    identification_id = fields.Many2one('ir.attachment', string='Identification')
