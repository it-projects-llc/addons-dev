# coding: utf-8
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request
# import wdb

class WebsiteSaleExtended(WebsiteSale):

    @http.route()
    def address(self, **kw):
        address_super = super(WebsiteSaleExtended, self).address(**kw)
        partner = 'partner_id' in address_super.qcontext and address_super.qcontext['partner_id'] > 0 and \
                  request.env['res.partner'].browse(address_super.qcontext['partner_id'])

        address_super.qcontext.update({
            'gender': partner and partner.gender,
            'genders': [('male', 'Male'), ('female', 'Female')],
            'identification_id': partner and partner.identification_id,
        })
        # address_super.qcontext
        # wdb.set_trace()
        return address_super

    @http.route()
    def checkout(self, **post):
        # wdb.set_trace()
        checkout_super = super(WebsiteSaleExtended, self).checkout(**post)

        return checkout_super

    def _get_mandatory_fields(self):
        fields_super = super(WebsiteSaleExtended, self)._get_mandatory_fields()
        return fields_super + ["gender"]

    def _checkout_form_save(self, mode, checkout, all_values):
        checkout_super = super(WebsiteSaleExtended, self)._checkout_form_save(mode, checkout, all_values)

        wdb.set_trace()
        partner = request.env['res.partner'].browse(int(all_values['partner_id']))
        partner.write({
            'gender': all_values['gender'],
            # 'identification_id': all_values['identification_id'],
        })
        return checkout_super
