# -*- coding: utf-8 -*-
from openerp import models, fields, api


class FleetBookingApproveMaintenanceWizard(models.TransientModel):
    _name = "fleet_booking.approve_maintenance_wizard"

    @api.model
    def _default_journal(self):
        return self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)

    journal_id = fields.Many2one('account.journal', string='Journal',
                                 required=True, readonly=True,
                                 default=_default_journal)

    @api.multi
    def create_entries(self):
        pass
