# coding: utf-8
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request


class WebsiteSaleExtended(WebsiteSale):

    @http.route()
    def address(self, **kw):
        address_super = super(WebsiteSaleExtended, self).address(**kw)
        partner_ID = 'partner_id' in address_super.qcontext and address_super.qcontext['partner_id']
        partner = partner_ID > 0 and request.env['res.partner'].sudo().browse(partner_ID)
        identification = partner and partner.identification_id
        attachments = partner and request.env['ir.attachment'].search([('res_id', '=', partner_ID),
                                                                       ('res_model', '=', "res.partner")]) or []

        address_super.qcontext.update({
            'gender': partner and partner.gender,
            'genders': [('male', 'Male'), ('female', 'Female')],
            'identification_id': partner and partner.identification_id,
            'attachments': attachments,
            'identification': identification,
        })
        return address_super

    @http.route()
    def checkout(self, **post):
        checkout_super = super(WebsiteSaleExtended, self).checkout(**post)

        return checkout_super

    def _get_mandatory_fields(self):
        fields_super = super(WebsiteSaleExtended, self)._get_mandatory_fields()
        return fields_super + ["gender"]

    def _checkout_form_save(self, mode, checkout, all_values):
        checkout_super = super(WebsiteSaleExtended, self)._checkout_form_save(mode, checkout, all_values)


        partner = request.env['res.partner'].browse(checkout_super)
        uploaded = request.env['ir.attachment'].search([('datas_fname', '=', all_values['identification_id']),
                                                        ('res_id', '=', partner.id),
                                                        ('res_model', '=', "res.partner")]) or []
        identification = len(uploaded) and uploaded[0].id or 'identification_id_select' in all_values and \
                                                             all_values['identification_id_select'] and \
                                                             int(all_values['identification_id_select'])

        partner.sudo().write({
            'gender': all_values['gender'],
            'identification_id': identification
        })
        return checkout_super
