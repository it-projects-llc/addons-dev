# -*- coding: utf-8 -*-
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class FleetRemoveVehicleWizard(models.TransientModel):
    _name = "fleet_booking.remove_vehicle_wizard"

    @api.model
    def _default_journal(self):
        return self.env['account.journal'].search([('type', '=', 'sale')], limit=1)

    journal_id = fields.Many2one('account.journal', string='Journal',
                                 required=True,
                                 default=_default_journal)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Choose Vehicle', required=True,
                              domain=lambda self: [('state_id', '=', self.env.ref('fleet_rental_document.vehicle_state_active').id)])

    removal_reason = fields.Selection([('damage', 'Damage'),
                                       ('sold', 'Sold'),
                                       ('end-of-life', 'End-of-Life')],
                                      string='Removal reason', required=True)
    selling_price = fields.Float(string='Selling price')
    move_line_ids = fields.One2many('fleet_booking.remove_move_line', 'remove_id')

    @api.multi
    def action_remove(self):
        partner_id = self.vehicle_id.partner_id.id
        move_date = fields.Date.context_today(self)
        move_lines = []

        for line in self.move_line_ids:
            move_line = {
                'name': self.vehicle_id.name + ' remove',
                'account_id': line.account_id.id,
                'debit': line.debit,
                'credit': line.credit,
                'journal_id': self.journal_id.id,
                'partner_id': partner_id,
                'date': move_date,
            }
            move_lines.append(move_line)

        move_vals = {
            'date': move_date,
            'journal_id': self.journal_id.id,
            'line_ids': [(0, 0, move_line) for move_line in move_lines],
        }

        move = self.env['account.move'].create(move_vals)
        self.vehicle_id.active = False
        self.vehicle_id.removal_reason= self.removal_reason
        self.vehicle_id.selling_price = self.selling_price


class FleetRemoveMoveLine(models.TransientModel):
    _name = "fleet_booking.remove_move_line"

    account_id = fields.Many2one('account.account', string='Account', require=True)
    debit = fields.Float(default=0.0, digits_compute=dp.get_precision('Product Price'), require=True)
    credit = fields.Float(default=0.0, digits_compute=dp.get_precision('Product Price'), require=True)

    remove_id = fields.Many2one('fleet_booking.remove_vehicle_wizard')
