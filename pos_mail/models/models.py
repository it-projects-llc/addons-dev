# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    send_receipt_by_mail = fields.Boolean('Mail a Receipt')

    @api.model
    def send_receipt_via_mail(self, partner_id, body_from_ui, pos_reference):

        partner = self.env['res.partner'].browse(partner_id)

        name = partner.name + ' POS Receipt'

        base64_pdf = self.env['ir.actions.report']._run_wkhtmltopdf(
            [body_from_ui.encode()],
            landscape=False,
            specific_paperformat_args={'data-report-margin-top': 10, 'data-report-header-spacing': 10}
        )

        order = self.env['pos.order'].search([('pos_reference', '=', pos_reference)])

        attachment = self.env['ir.attachment'].create({
            'name': name,
            'datas_fname': name + '.pdf',
            'type': 'binary',
            'db_datas': base64.encodestring(base64_pdf),
            'res_model': 'pos.order',
            'res_id': order and order.id or False,
        })

        # wizard model creation
        composer = self.env['mail.compose.message'].create({
            'partner_ids': [(6, False, [partner.id])],
            'attachment_ids': [(6, False, [attachment.id])],
            'notify': True,
        })
        composer.send_mail()

        return
