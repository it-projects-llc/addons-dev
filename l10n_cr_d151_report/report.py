from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime


class D151Report(models.TransientModel):
    _name = "d151.wizard"
    _description = "D151 Report"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Start Date', default=lambda *a: datetime.now().
        date().replace(month=1, day=1).strftime('%Y-%m-%d'))
    date_to = fields.Date(string='End Date', default=lambda *a: datetime.now().strftime('%Y-%m-%d'))
    partner_ids = fields.Many2many('res.partner', string='Partners')
    cr_d151_category_ids = fields.Many2many('account.cr.d151.category', string='D151 categories')
    show_details = fields.Boolean(default=False)

    @api.multi
    def print_xls_report(self):
        data = self.read()[0]
        raw_data = self.get_filtered_data_for_report()
        json_data = self.get_json_data(raw_data)
        json_data = map(self.get_amounts, json_data)
        json_data = map(self.check_min_amount, json_data)
        json_data = filter(None, json_data)
        json_data = map(self.filter_data, json_data)
        if not json_data:
            raise UserError('There are no reports for specified criteria.')
        data['filtered_data'] = json_data

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
        res = []
        for aml_d151_category in data.mapped('cr_d151_category_id'):
            aml_dict = {
                'cr_d151_category_name': aml_d151_category.name,
                'cr_d151_category_code': aml_d151_category.code_id.name,
                'cr_d151_category_min_amount': aml_d151_category.min_amount,
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

    @staticmethod
    def get_amounts(data):
        category_amount = 0
        for p in data['partners']:
            partner_amount = 0
            for a in p['amls']:
                partner_amount += float(a['amount'])
            p.update({ 'partner_amount' : partner_amount})
            category_amount += partner_amount
        data.update({'category_amount': category_amount})
        return data

    @staticmethod
    def filter_data(data):
        data['partners'] = [p for p in data['partners'] if p['amls']]
        if not data['partners']:
            return
        return data

    @staticmethod
    def check_min_amount(data):
        min_amount = float(data['cr_d151_category_min_amount'])
        data['partners'] = [p for p in data['partners'] if float(p['partner_amount'] >= min_amount)]
        if not data['partners']:
            return
        return data
