# -*- coding: utf-8 -*-
import openerp
from openerp import models, fields, api


class FleetRentalItemToCheck(models.Model):
    _name = 'fleet_rental.item_to_check'

    name = fields.Char(string='Item', help='Item to be checked before and after rent', required=True)


class FleetRentalCheckLine(models.Model):
    _name = 'fleet_rental.check_line'

    item_id = fields.Many2one('fleet_rental.item_to_check', string='Item', ondelete='restrict', required=True, readonly=True)
    document_id = fields.Many2one('fleet_rental.document', string='Document', ondelete='cascade', required=True)
    exit_check_yes = fields.Boolean(string='OK (on out)', default=False)
    exit_check_no = fields.Boolean(string='NOT ok (on out)', default=False)
    return_check_yes = fields.Boolean(string='OK (on return)', default=False)
    return_check_no = fields.Boolean(string='NOT ok (on return)', default=False)

    @api.onchange('exit_check_yes')
    def _onchange_exit_check_yes(self):
        if self.exit_check_yes:
            self.exit_check_no = False

    @api.onchange('exit_check_no')
    def _onchange_exit_check_no(self):
        if self.exit_check_no:
            self.exit_check_yes = False

    @api.onchange('return_check_yes')
    def _onchange_return_check_yes(self):
        if self.return_check_yes:
            self.return_check_no = False

    @api.onchange('return_check_no')
    def _onchange_return_check_no(self):
        if self.return_check_no:
            self.return_check_yes = False


class FleetRentalSVGVehiclePart(models.Model):
    _name = 'fleet_rental.svg_vehicle_part'

    name = fields.Char(string='Part name')
    path_ID = fields.Char(string='svg path id', required=True)


class FleetRentalSVGVehiclePartLine(models.Model):
    _name = 'fleet_rental.svg_vehicle_part_line'

    part_id = fields.Many2one('fleet_rental.svg_vehicle_part', string='Part', ondelete='restrict', required=True, readonly=True)
    path_ID = fields.Char(related="part_id.path_ID")
    document_id = fields.Many2one('fleet_rental.document', string='Document', ondelete='cascade', required=True)
    state = fields.Selection([('operative', 'Operative'),
                              ('broken', 'Broken')],
                             string='State',
                             default='operative')
