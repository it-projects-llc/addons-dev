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
        partner_ID = 'partner_id' in address_super.qcontext and address_super.qcontext['partner_id'] or \
                     'partner_id' in kw and int(kw['partner_id'])

        partner = partner_ID > 0 and request.env['res.partner'].sudo().browse(partner_ID)
        attachments = partner and request.env['ir.attachment'].sudo().search([('res_id', '=', partner_ID),
                                                                              ('res_model', '=', "res.partner")]) or []


        address_super.qcontext.update({
            'gender': partner and partner.gender,
            'genders': [('male', 'Male'), ('female', 'Female')],
            'identification_id': partner and partner.identification_id,
            'attachments': attachments,
        })
        return address_super

    def _get_mandatory_fields(self):
        fields_super = super(WebsiteSaleExtended, self)._get_mandatory_fields()
        return fields_super + ["gender"]

    def _checkout_form_save(self, mode, checkout, all_values):
        checkout_super = super(WebsiteSaleExtended, self)._checkout_form_save(mode, checkout, all_values)
        partner = request.env['res.partner'].sudo().browse(checkout_super)

        if 'identification_id' in all_values and 'identification_file' in all_values:
            ir_attachment_env = request.env['ir.attachment'].sudo()
            file_name = all_values['identification_id']
            file_data = all_values['identification_file']
            attachment = ir_attachment_env.search([('datas_fname', '=', file_name),
                                                   ('res_id', '=', partner.id),
                                                   ('res_model', '=', "res.partner")])
            if len(attachment):
                attachment[0].write({
                    'type': 'binary',
                    'name': file_name,
                    'datas': file_data,
                })
                attachment = attachment[0]
            else:
                attachment = ir_attachment_env.create({
                    'type': 'binary',
                    'name': file_name,
                    'datas': file_data,
                    'res_id': partner.id,
                    'datas_fname': file_name,
                    'res_model': "res.partner",
                })
            partner.write({
                'identification_id': attachment.id,
            })

        elif 'identification_id_select' in all_values:
            partner.write({
                'identification_id': int(all_values['identification_id_select']),
            })

        partner.sudo().write({
            'gender': all_values['gender'],
            'identification_id': partner.identification_id.id
        })

        return checkout_super
