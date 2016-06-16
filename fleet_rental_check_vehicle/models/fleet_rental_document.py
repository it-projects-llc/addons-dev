# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api

class FleetRentalDocument(models.Model):
    _inherit = 'fleet_rental.document'

    check_line_ids = fields.One2many('fleet_rental.check_line', string='Vehicle rental checklist')
