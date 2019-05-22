# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    send_receipt_by_mail = fields.Boolean('Mail a Receipt')

    @api.model
    def send_receipt_via_mail(self, partner_id, body):

        partner = self.env['res.partner'].browse(partner_id)
        pdf = self.env['ir.actions.report']._run_wkhtmltopdf(
            [body.encode()],
            landscape=True,
            specific_paperformat_args={'data-report-margin-top': 10, 'data-report-header-spacing': 10}
        )
        name = partner.name + ' POS Receipt'
        attachment = self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'db_datas': pdf,
            'res_id': partner.id,
        })

        # wizard model creation
        composer = self.env['mail.compose.message'].create({
            'partner_ids': [(6, False, [partner.id])],
            'attachment_ids': [(6, False, [attachment.id])],
            'notify': True,
        })
        composer.send_mail()

        return
