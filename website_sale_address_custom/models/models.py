# coding: utf-8
# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = "res.partner"

    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], default='male', string="Gender")
    identification_id = fields.Many2one('ir.attachment', string='Identification')

    @api.model
    def upload_file(self, data=False):

        ir_attachment_env = self.env['ir.attachment']
        attachment = ir_attachment_env.search([('datas_fname', '=', data['name']),
                                               ('res_id', '=', int(data['uid'])),
                                               ('res_model', '=', "res.partner")])
        if len(attachment):
            attachment[0].write({
                'type': 'binary',
                'name': data['name'],
                'datas': data['data'],
            })
            attachment = attachment[0]
        else:
            attachment = ir_attachment_env.create({
                'type': 'binary',
                'name': data['name'],
                'datas': data['data'],
                'res_id': int(data['uid']),
                'res_model': "res.partner",
                'datas_fname': data['name'],
            })

        partner = self.browse(int(data['uid']))
        partner.write({
            'identification_id': attachment.id,
        })

        return attachment.id
