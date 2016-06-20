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
    check_yes = fields.Boolean(string='yes', default=False)
    check_no = fields.Boolean(string='no', default=False)

    @api.multi
    def write(self, vals):
        # there should be 'yes' or 'no'
        if vals.get('check_yes'):
            vals.update({'check_no': False})
        if vals.get('check_no'):
            vals.update({'check_yes': False})
        return super(FleetRentalCheckLine, self).write(vals)
