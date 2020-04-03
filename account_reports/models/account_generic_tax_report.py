# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api
from odoo.tools.translate import _
from odoo.tools.misc import formatLang


class generic_tax_report(models.AbstractModel):
    _inherit = 'account.report'
    _name = 'account.generic.tax.report'
    _description = 'Generic Tax Report'

    filter_multi_company = None
    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}
    filter_all_entries = False
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}

    def _get_columns_name(self, options):
        columns_header = [{}, {'name': '%s \n %s' % (_('NET'), self.format_date(options)), 'class': 'number', 'style': 'white-space: pre;'}, {'name': _('TAX'), 'class': 'number'}]
        if options.get('comparison') and options['comparison'].get('periods'):
            for p in options['comparison']['periods']:
                columns_header += [{'name': '%s \n %s' % (_('NET'), p.get('string')), 'class': 'number', 'style': 'white-space: pre;'}, {'name': _('TAX'), 'class': 'number'}]
        return columns_header

    def _set_context(self, options):
        ctx = super(generic_tax_report, self)._set_context(options)
        ctx['strict_range'] = True
        return ctx

    def _sql_cash_based_taxes(self):
        sql = """SELECT tax.id, SUM(CASE WHEN tax.type_tax_use = 'sale' THEN -"account_move_line".tax_base_amount ELSE "account_move_line".tax_base_amount END), SUM("account_move_line".balance) FROM account_tax tax, %s WHERE tax.id = "account_move_line".tax_line_id AND %s AND tax.tax_exigibility = 'on_payment' and "account_move_line".tax_exigible GROUP BY tax.id"""
        return sql

    def _sql_tax_amt_regular_taxes(self):
        sql = """SELECT "account_move_line".tax_line_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                    FROM account_tax tax, %s
                    WHERE %s AND tax.tax_exigibility = 'on_invoice' AND tax.id = "account_move_line".tax_line_id
                    GROUP BY "account_move_line".tax_line_id"""
        return sql

    def _sql_net_amt_regular_taxes(self):
        sql = """SELECT r.account_tax_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                 FROM %s
                 INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
                 INNER JOIN account_tax t ON (r.account_tax_id = t.id)
                 WHERE %s AND t.tax_exigibility = 'on_invoice' GROUP BY r.account_tax_id"""
        return sql

    def _compute_from_amls(self, options, taxes, period_number):
        sql = self._sql_cash_based_taxes()
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['periods'][period_number]['net'] = result[1]
                taxes[result[0]]['periods'][period_number]['tax'] = result[2]
                taxes[result[0]]['show'] = True
        sql = self._sql_net_amt_regular_taxes()
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['periods'][period_number]['net'] = result[1]
                taxes[result[0]]['show'] = True
        sql = self._sql_tax_amt_regular_taxes()
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['periods'][period_number]['tax'] = result[1]
                taxes[result[0]]['show'] = True

    def _get_type_tax_use_string(self, value):
        return [option[1] for option in self.env['account.tax']._fields['type_tax_use'].selection if option[0] == value][0]

    def _get_type_tax_use_string(self, value):
        return [option[1] for option in self.env['account.tax']._fields['type_tax_use'].selection if option[0] == value][0]

    @api.model
    def _get_lines(self, options, line_id=None):
        taxes = {}
        for tax in self.env['account.tax'].with_context(active_test=False).search([]):
            taxes[tax.id] = {'obj': tax, 'show': False, 'periods': [{'net': 0, 'tax': 0}]}
            for period in options['comparison'].get('periods'):
                taxes[tax.id]['periods'].append({'net': 0, 'tax': 0})
        period_number = 0
        self._compute_from_amls(options, taxes, period_number)
        for period in options['comparison'].get('periods'):
            period_number += 1
            self.with_context(date_from=period.get('date_from'), date_to=period.get('date_to'))._compute_from_amls(options, taxes, period_number)
        lines = []
        types = ['sale', 'purchase', 'adjustment']
        groups = dict((tp, {}) for tp in types)
        for key, tax in taxes.items():
            if tax['obj'].type_tax_use == 'none':
                continue
            if tax['obj'].children_tax_ids:
                tax['children'] = []
                for child in tax['obj'].children_tax_ids:
                    if child.type_tax_use != 'none':
                        continue
                    tax['children'].append(taxes[child.id])
            if tax['obj'].children_tax_ids and not tax.get('children'):
                continue
            groups[tax['obj'].type_tax_use][key] = tax
        line_id = 0
        for tp in types:
            if not any([tax.get('show') for key, tax in groups[tp].items()]):
                continue
            sign = tp == 'sale' and -1 or 1
            lines.append({
                    'id': tp,
                    'name': self._get_type_tax_use_string(tp),
                    'unfoldable': False,
                    'columns': [{} for k in range(0, 2 * (period_number + 1) or 2)],
                    'level': 1,
                })
            for key, tax in sorted(groups[tp].items(), key=lambda k: k[1]['obj'].sequence):
                if tax['show']:
                    columns = []
                    for period in tax['periods']:
                        columns += [{'name': self.format_value(period['net'] * sign), 'style': 'white-space:nowrap;'},{'name': self.format_value(period['tax'] * sign), 'style': 'white-space:nowrap;'}]
                    lines.append({
                        'id': tax['obj'].id,
                        'name': tax['obj'].name + ' (' + str(tax['obj'].amount) + ')',
                        'unfoldable': False,
                        'columns': columns,
                        'level': 4,
                        'caret_options': 'account.tax',
                    })
                    for child in tax.get('children', []):
                        columns = []
                        for period in child['periods']:
                            columns += [{'name': self.format_value(period['net'] * sign), 'style': 'white-space:nowrap;'},{'name': self.format_value(period['tax'] * sign), 'style': 'white-space:nowrap;'}]
                        lines.append({
                            'id': child['obj'].id,
                            'name': '   ' + child['obj'].name + ' (' + str(child['obj'].amount) + ')',
                            'unfoldable': False,
                            'columns': columns,
                            'level': 4,
                            'caret_options': 'account.tax',
                        })
            line_id += 1
        return lines

    @api.model
    def _get_report_name(self):
        return _('Tax Report')
