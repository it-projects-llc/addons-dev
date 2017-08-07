from odoo import models, fields

class D151Report(models.TransientModel):
    _name = "d151.report"
    _description = "D151 Report"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    partner_ids = fields.Many2many('res.partner', string='Partners')
    cr_d151_category_ids = fields.Many2many('account.cr.d151.category', string='D151 categories')
    show_details = fields.Boolean(default=False)

    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to'])[0])
        return self.env['report'].get_action(self, 'l10n_cr_d151_report.d151_report', data=data)