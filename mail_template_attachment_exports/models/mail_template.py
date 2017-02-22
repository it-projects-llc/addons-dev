# -*- coding: utf-8 -*-
from odoo import models, fields


class MailTemplate(models.Model):
    _inherit = "mail.template"

    export_model_id = fields.Many2one('ir.model', 'Model', help="The type of document this template can be used with")
    export_model = fields.Char('Related Document Model', related='model_id.model', index=True, store=True, readonly=True)
    export_domain = fields.Char('Domain', help='Domain for data to be exported')
    export_fields_id = fields.Many2one('ir.exports', 'Fields', help='Fields to export')
    export_format = fields.Selection(
        [
            ('csv', 'CSV'),
            ('xsl', 'Excel'),
        ], string='Format',
        default='xsl',
        required=True,
        help='format of exporting file')
