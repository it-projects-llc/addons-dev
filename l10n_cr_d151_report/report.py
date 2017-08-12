from odoo import models, fields, api

class D151Report(models.TransientModel):
    _name = "d151.wizard"
    _description = "D151 Report"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    partner_ids = fields.Many2many('res.partner', string='Partners')
    cr_d151_category_ids = fields.Many2many('account.cr.d151.category', string='D151 categories')
    show_details = fields.Boolean(default=False)

    @api.multi
    def print_xls_report(self):
        data = self.read()[0]
        aml_data = self.get_filtered_data_for_report()
        aml_data = self.get_json_data(aml_data)
        data['filtered_data'] = aml_data

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'l10n_cr_d151_report.d151_report_template',
            'datas': data,
            'report_file': 'd151_report.xls',
        }

    def get_filtered_data_for_report(self):
        account_move_lines = self.env['account.move.line'].search([('company_id', '=', self.company_id.id)])
        if self.date_from:
            account_move_lines = account_move_lines.search([('date', '>=', self.date_from)])
        if self.date_to:
            account_move_lines = account_move_lines.search([('date', '<=', self.date_to)])
        if self.partner_ids:
            account_move_lines = account_move_lines.search([('partner_id', 'in', self.partner_ids.ids)])
        if self.cr_d151_category_ids:
            account_move_lines = account_move_lines.search([('cr_d151_category_id', 'in', self.cr_d151_category_ids.ids)])
        return account_move_lines

    def get_json_data(self, data):
        #TODO: partner total amount <= min_amount filter
        res = []
        for aml_d151_category in data.mapped('cr_d151_category_id'):
            aml_dict = {
                'cr_d151_category_name': aml_d151_category.name,
                'cr_d151_category_code': aml_d151_category.code_id.name,
                'partners': []
            }
            partners_filtered = data.mapped('partner_id')
            for index, partner in enumerate(partners_filtered):
                aml_dict['partners'].append({
                    'partner': partner.name,
                    'ref': partner.ref if partner.ref else '',
                    'amls': []
                })
                for i in data:
                    if (i.cr_d151_category_id.id == aml_d151_category.id) and (i.partner_id.id == partner.id):
                        aml_dict['partners'][index]['amls'].append({
                            'date': i.move_id.date,
                            'move': i.move_id.name,
                            'reference': i.move_id.ref if i.move_id.ref else '',
                            'journal': i.journal_id.name,
                            'account': i.account_id.name,
                            'amount': (i.debit - i.credit)*aml_d151_category.sign
                        })
            res.append(aml_dict)
        return res
