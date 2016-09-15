# -*- coding: utf-8 -*-
from openerp import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fleet_vehicle_log_services_ids = fields.Many2one('fleet.vehicle.log.services')
    fleet_vehicle_id = fields.Many2one('fleet.vehicle')

    @api.multi
    def action_move_create(self):
        result = super(AccountInvoice, self).action_move_create()
        # Why does odoo account_asset deactivate existing assets?
        # It is undesirable in case of fleet_booking vehicle asset
        # So we activate deactivated records in the same method
        for inv in self:
            if inv.number and inv.invoice_line_ids[0].fleet_rental_document_id:
                asset_ids = self.env['account.asset.asset'].sudo().with_context(active_test=False).search(
                    [('invoice_id', '=', inv.id), ('company_id', '=', inv.company_id.id)])
                if asset_ids:
                    asset_ids.write({'active': True})
        return result
