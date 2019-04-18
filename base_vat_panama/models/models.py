# -*- coding: utf-8 -*-

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _split_vat(self, vat):
        vat_country = vat[:3].lower()
        if vat_country == 'ruc':
            return 'pacustom', vat
        return super(ResPartner, self)._split_vat(vat)

    def check_vat_pacustom(self, vat):
        return True
