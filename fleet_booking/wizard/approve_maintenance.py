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
        service = self.env['fleet.vehicle.log.services'].browse(self._context.get('active_id'))
        service.service_line_ids.filtered(
            lambda r: not r.move_check and r.debit_account and r.credit_account
        ).create_move(self.journal_id.id)
        if self.env['fleet.vehicle.service.line'].search_count([('move_check', '=', False),
                                                                ('service_log_id', '=', service.id)]) == 0:
            service.write({'state': 'paid'})
