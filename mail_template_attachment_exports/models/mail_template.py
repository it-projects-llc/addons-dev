# -*- coding: utf-8 -*-
import base64
import operator

from odoo import models, fields as odoo_fields, api
from odoo.addons.web.controllers.main import CSVExport, ExcelExport
from odoo.tools.safe_eval import safe_eval


class MailTemplate(models.Model):
    _inherit = "mail.template"

    export_model_id = odoo_fields.Many2one('ir.model', 'Model', help="The type of document this template can be used with")
    export_model = odoo_fields.Char('Related Document Model', related='export_model_id.model', index=True, store=True, readonly=True)
    export_domain = odoo_fields.Char('Domain', help='Domain for data to be exported')
    export_fields_id = odoo_fields.Many2one('ir.exports', 'Fields', help='Fields to export')
    export_format = odoo_fields.Selection(
        [
            ('csv', 'CSV'),
            ('xls', 'Excel'),
        ], string='Format',
        default='xls',
        required=True,
        help='format of exporting file')
    export_import_compat = odoo_fields.Boolean(
        'Import-Compatible Export',
        default=True,
    )

    @api.model
    def send_mail_cron(self, template_id, *args):
        """Wrapping for send_mail to call in cron,
        because cron can call @api.model only"""
        return self.browse(template_id).send_mail(*args)

    @api.multi
    def generate_email(self, res_ids, fields=None):
        results = super(MailTemplate, self).generate_email(res_ids, fields=fields)
        template = self
        if not template.export_model_id:
            return results

        multi_mode = True
        if isinstance(res_ids, (int, long)):
            res_ids = [res_ids]
            multi_mode = False

        if not multi_mode:
            results = {res_ids[0]: results}

        # While in original generate_email there are one report per each
        # res_id, we need only one export file for all emails because it
        # doesn't depend on res_id

        # code is based on *base* method in web/controllers/main.py
        cls = CSVExport if self.export_format == 'csv' else ExcelExport
        cls = cls()
        domain = safe_eval(self.export_domain)
        model = self.export_model
        Model = self.env[model]
        records = Model.search(domain)

        # We ignore fields value in method args. Shall we change it?
        fields = self.env['mail_template_attachment_exports.abstract_export']\
                     .namelist(model, template.export_fields_id.id)

        field_names = map(operator.itemgetter('name'), fields)
        import_data = records.export_data(field_names, cls.raw_data).get('datas', [])

        if self.export_import_compat:
            columns_headers = field_names
        else:
            columns_headers = [val['label'].strip() for val in fields]

        data = cls.from_data(columns_headers, import_data)
        report_name = cls.filename(model)

        for res_id, values in results.iteritems():
            result = base64.b64encode(data)
            values.setdefault('attachments', [])
            values['attachments'].append((report_name, result))

        return multi_mode and results or results[res_ids[0]]
