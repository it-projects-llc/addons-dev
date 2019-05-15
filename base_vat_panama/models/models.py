# -*- coding: utf-8 -*-
# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ruc = fields.Char('RUC')
    dv = fields.Char('DV')

    def _split_vat(self, vat):
        vat_country = vat[:3].lower()
        # Panamanian VaT numbers start with 'RUC'
        if vat_country == 'ruc':
            return 'pacustom', vat
        return super(ResPartner, self)._split_vat(vat)

    def check_vat_pacustom(self, vat):
        return True
