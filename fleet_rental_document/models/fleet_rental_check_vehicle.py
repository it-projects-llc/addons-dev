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
    exit_check_yes = fields.Boolean(string='yes', default=False)
    exit_check_no = fields.Boolean(string='no', default=False)
    return_check_yes = fields.Boolean(string='yes', default=False)
    return_check_no = fields.Boolean(string='no', default=False)

    @api.multi
    def write(self, vals):
        # there should be 'yes' or 'no'
        if vals.get('exit_check_yes'):
            vals.update({'exit_check_no': False})
        if vals.get('exit_check_no'):
            vals.update({'exit_check_yes': False})
        if vals.get('return_check_yes'):
            vals.update({'return_check_no': False})
        if vals.get('return_check_no'):
            vals.update({'return_check_yes': False})
        return super(FleetRentalCheckLine, self).write(vals)
