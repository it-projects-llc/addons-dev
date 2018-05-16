# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    barcode = fields.Char(
        string="Barcode")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
