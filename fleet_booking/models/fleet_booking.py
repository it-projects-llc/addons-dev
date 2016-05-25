# -*- coding: utf-8 -*-

from openerp import api, fields, models


class HrDepartment(models.Model):

    _name = "fleet_booking.branch"
    _inherit = 'hr.department'

    city = fields.Char(string='City')
    phone = fields.Char(string='Phone')
    branch_target = fields.Char(string='Branch Target')
