# -*- coding: utf-8 -*-
# ©  2015 ERGOBIT Consulting (https://www.ergobit.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    legal_holidays_status_id_n1 = fields.Many2one('hr.holidays.status', 'Legal Leave Status N-1', )
    legal_holidays_status_id_n2 = fields.Many2one('hr.holidays.status', 'Legal Leave Status N-2', )
