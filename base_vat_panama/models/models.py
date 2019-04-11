# -*- coding: utf-8 -*-

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _split_vat(self, vat):
        vat_country = vat[:3].lower()
        import wdb
        wdb.set_trace()
        if vat_country == 'ruc':
            return 'pa', vat
        return super(ResPartner, self)._split_vat(vat)

    # @api.model
    # def simple_vat_check(self, country_code, vat_number):
    #     '''
    #     Check the VAT number depending of the country.
    #     http://sima-pc.com/nif.php
    #     '''
    #     if not ustr(country_code).encode('utf-8').isalpha():
    #         return False
    #     check_func_name = 'check_vat_' + country_code
    #     check_func = getattr(self, check_func_name, None) or getattr(vatnumber, check_func_name, None)
    #     if not check_func:
    #         # No VAT validation available, default to check that the country code exists
    #         if country_code.upper() == 'EU':
    #             # Foreign companies that trade with non-enterprises in the EU
    #             # may have a VATIN starting with "EU" instead of a country code.
    #             return True
    #         country_code = _eu_country_vat_inverse.get(country_code, country_code)
    #         return bool(self.env['res.country'].search([('code', '=ilike', country_code)]))
    #     return check_func(vat_number)
    #
    #
    # @api.constrains("vat")
    # def check_vat(self):
    #     if self.env.context.get('company_id'):
    #         company = self.env['res.company'].browse(self.env.context['company_id'])
    #     else:
    #         company = self.env.user.company_id
    #     if company.vat_check_vies:
    #         # force full VIES online check
    #         check_func = self.vies_vat_check
    #     else:
    #         # quick and partial off-line checksum validation
    #         check_func = self.simple_vat_check
    #     for partner in self:
    #         if not partner.vat:
    #             continue
    #         vat_country, vat_number = self._split_vat(partner.vat)
    #         if not check_func(vat_country, vat_number):
    #             _logger.info("Importing VAT Number [%s] is not valid !" % vat_number)
    #             msg = partner._construct_constraint_msg()
    #             raise ValidationError(msg)

    def check_vat_pa(self, vat):
        import wdb
        wdb.set_trace()
        return True
