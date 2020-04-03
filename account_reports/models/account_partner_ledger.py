# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _, fields
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date
from datetime import datetime, timedelta


class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.report"
    _name = "account.partner.ledger"
    _description = "Partner Ledger"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_year'}
    filter_cash_basis = False
    filter_all_entries = False
    filter_unfold_all = False
    filter_account_type = [{'id': 'receivable', 'name': _('Receivable'), 'selected': False}, {'id': 'payable', 'name': _('Payable'), 'selected': False}]
    filter_unreconciled = False
    filter_partner = True

    def _get_templates(self):
        templates = super(ReportPartnerLedger, self)._get_templates()
        templates['line_template'] = 'account_reports.line_template_partner_ledger_report'
        return templates

    def _get_columns_name(self, options):
        columns = [
            {},
            {'name': _('JRNL')},
            {'name': _('Account')},
            {'name': _('Ref')},
            {'name': _('Due Date'), 'class': 'date'},
            {'name': _('Matching Number')},
            {'name': _('Initial Balance'), 'class': 'number'},
            {'name': _('Debit'), 'class': 'number'},
            {'name': _('Credit'), 'class': 'number'}]

        if self.user_has_groups('base.group_multi_currency'):
            columns.append({'name': _('Amount Currency'), 'class': 'number'})

        columns.append({'name': _('Balance'), 'class': 'number'})

        return columns

    def _set_context(self, options):
        ctx = super(ReportPartnerLedger, self)._set_context(options)
        ctx['strict_range'] = True
        return ctx

    def _do_query_group_by_account(self, options, line_id):
        account_types = [a.get('id') for a in options.get('account_type') if a.get('selected', False)]
        if not account_types:
            account_types = [a.get('id') for a in options.get('account_type')]
        # Create the currency table.
        user_company = self.env.user.company_id
        companies = self.env['res.company'].search([])
        rates_table_entries = []
        for company in companies:
            if company.currency_id == user_company.currency_id:
                rate = 1.0
            else:
                rate = self.env['res.currency']._get_conversion_rate(
                    company.currency_id, user_company.currency_id, user_company, datetime.today())
            rates_table_entries.append((company.id, rate, user_company.currency_id.decimal_places))
        currency_table = ','.join('(%s, %s, %s)' % r for r in rates_table_entries)
        with_currency_table = 'WITH currency_table(company_id, rate, precision) AS (VALUES %s)' % currency_table

        # Sum query
        debit_field = 'debit_cash_basis' if options.get('cash_basis') else 'debit'
        credit_field = 'credit_cash_basis' if options.get('cash_basis') else 'credit'
        balance_field = 'balance_cash_basis' if options.get('cash_basis') else 'balance'
        tables, where_clause, params = self.env['account.move.line']._query_get(
            [('account_id.internal_type', 'in', account_types)])
        query = '''
            SELECT
                \"account_move_line\".partner_id,
                SUM(ROUND(\"account_move_line\".''' + debit_field + ''' * currency_table.rate, currency_table.precision))     AS debit,
                SUM(ROUND(\"account_move_line\".''' + credit_field + ''' * currency_table.rate, currency_table.precision))    AS credit,
                SUM(ROUND(\"account_move_line\".''' + balance_field + ''' * currency_table.rate, currency_table.precision))   AS balance
            FROM %s
            LEFT JOIN currency_table                    ON currency_table.company_id = \"account_move_line\".company_id
            WHERE %s
            AND \"account_move_line\".partner_id IS NOT NULL
            GROUP BY \"account_move_line\".partner_id
        ''' % (tables, where_clause)
        if line_id:
            query = query.replace('WHERE', 'WHERE \"account_move_line\".partner_id = %s AND ')
            params = [str(line_id)] + params
        if options.get("unreconciled"):
            query = query.replace("WHERE", 'WHERE \"account_move_line\".full_reconcile_id IS NULL AND ')
        self._cr.execute(with_currency_table + query, params)
        query_res = self._cr.dictfetchall()
        return dict((res['partner_id'], res) for res in query_res)

    def _group_by_partner_id(self, options, line_id):
        partners = {}
        account_types = [a.get('id') for a in options.get('account_type') if a.get('selected', False)]
        if not account_types:
            account_types = [a.get('id') for a in options.get('account_type')]
        date_from = options['date']['date_from']
        results = self._do_query_group_by_account(options, line_id)
        initial_bal_results = self.with_context(
            date_from=False, date_to=fields.Date.from_string(date_from) + timedelta(days=-1)
        )._do_query_group_by_account(options, line_id)
        context = self.env.context
        base_domain = [('date', '<=', context['date_to']), ('company_id', 'in', context['company_ids']), ('account_id.internal_type', 'in', account_types)]
        base_domain.append(('date', '>=', date_from))
        if context['state'] == 'posted':
            base_domain.append(('move_id.state', '=', 'posted'))
        if options.get('unreconciled'):
            base_domain.append(('full_reconcile_id', '=', False))
        for partner_id, result in results.items():
            domain = list(base_domain)  # copying the base domain
            domain.append(('partner_id', '=', partner_id))
            partner = self.env['res.partner'].browse(partner_id)
            partners[partner] = result
            partners[partner]['initial_bal'] = initial_bal_results.get(partner.id, {'balance': 0, 'debit': 0, 'credit': 0})
            partners[partner]['balance'] += partners[partner]['initial_bal']['balance']
            partners[partner]['total_lines'] = 0
            if not context.get('print_mode'):
                partners[partner]['total_lines'] = self.env['account.move.line'].search_count(domain)
                offset = int(options.get('lines_offset', 0))
                limit = self.MAX_LINES
                partners[partner]['lines'] = self.env['account.move.line'].search(domain, order='date,id', limit=limit, offset=offset)
            else:
                partners[partner]['lines'] = self.env['account.move.line'].search(domain, order='date,id')

        # Add partners with an initial balance != 0 but without any AML in the selected period.
        prec = self.env.user.company_id.currency_id.rounding
        missing_partner_ids = set(initial_bal_results.keys()) - set(results.keys())
        for partner_id in missing_partner_ids:
            if not float_is_zero(initial_bal_results[partner_id]['balance'], precision_rounding=prec):
                partner = self.env['res.partner'].browse(partner_id)
                partners[partner] = {'balance': 0, 'debit': 0, 'credit': 0}
                partners[partner]['initial_bal'] = initial_bal_results[partner_id]
                partners[partner]['balance'] += partners[partner]['initial_bal']['balance']
                partners[partner]['lines'] = self.env['account.move.line']
                partners[partner]['total_lines'] = 0

        return partners

    @api.model
    def _get_lines(self, options, line_id=None):
        offset = int(options.get('lines_offset', 0))
        lines = []
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        if line_id:
            line_id = int(line_id.split('_')[1]) or None
        elif options.get('partner_ids') and len(options.get('partner_ids')) == 1:
            #If a default partner is set, we only want to load the line referring to it.
            partner_id = options['partner_ids'][0]
            line_id = partner_id
        if line_id:
            if 'partner_' + str(line_id) not in options.get('unfolded_lines', []):
                options.get('unfolded_lines', []).append('partner_' + str(line_id))

        grouped_partners = self._group_by_partner_id(options, line_id)
        sorted_partners = sorted(grouped_partners, key=lambda p: p.name or '')
        unfold_all = context.get('print_mode') and not options.get('unfolded_lines')
        total_initial_balance = total_debit = total_credit = total_balance = 0.0
        for partner in sorted_partners:
            debit = grouped_partners[partner]['debit']
            credit = grouped_partners[partner]['credit']
            balance = grouped_partners[partner]['balance']
            initial_balance = grouped_partners[partner]['initial_bal']['balance']
            total_initial_balance += initial_balance
            total_debit += debit
            total_credit += credit
            total_balance += balance
            columns = [self.format_value(initial_balance), self.format_value(debit), self.format_value(credit)]
            if self.user_has_groups('base.group_multi_currency'):
                columns.append('')
            columns.append(self.format_value(balance))
            # don't add header for `load more`
            if offset == 0:
                lines.append({
                    'id': 'partner_' + str(partner.id),
                    'name': partner.name,
                    'columns': [{'name': v} for v in columns],
                    'level': 2,
                    'trust': partner.trust,
                    'unfoldable': True,
                    'unfolded': 'partner_' + str(partner.id) in options.get('unfolded_lines') or unfold_all,
                    'colspan': 6,
                })
            user_company = self.env.user.company_id
            used_currency = user_company.currency_id
            if 'partner_' + str(partner.id) in options.get('unfolded_lines') or unfold_all:
                if offset == 0:
                    progress = initial_balance
                else:
                    progress = float(options.get('lines_progress', initial_balance))
                domain_lines = []
                amls = grouped_partners[partner]['lines']

                remaining_lines = 0
                if not context.get('print_mode'):
                    remaining_lines = grouped_partners[partner]['total_lines'] - offset - len(amls)

                for line in amls:
                    if options.get('cash_basis'):
                        line_debit = line.debit_cash_basis
                        line_credit = line.credit_cash_basis
                    else:
                        line_debit = line.debit
                        line_credit = line.credit
                    date = amls.env.context.get('date') or fields.Date.today()
                    line_currency = line.company_id.currency_id
                    line_debit = line_currency._convert(line_debit, used_currency, user_company, date)
                    line_credit = line_currency._convert(line_credit, used_currency, user_company, date)
                    progress_before = progress
                    progress = progress + line_debit - line_credit
                    caret_type = 'account.move'
                    if line.invoice_id:
                        caret_type = 'account.invoice.in' if line.invoice_id.type in ('in_refund', 'in_invoice') else 'account.invoice.out'
                    elif line.payment_id:
                        caret_type = 'account.payment'
                    domain_columns = [line.journal_id.code, line.account_id.code, self._format_aml_name(line),
                                      line.date_maturity and format_date(self.env, line.date_maturity) or '',
                                      line.full_reconcile_id.name or '', self.format_value(progress_before),
                                      line_debit != 0 and self.format_value(line_debit) or '',
                                      line_credit != 0 and self.format_value(line_credit) or '']
                    if self.user_has_groups('base.group_multi_currency'):
                        domain_columns.append(self.with_context(no_format=False).format_value(line.amount_currency, currency=line.currency_id) if line.amount_currency != 0 else '')
                    domain_columns.append(self.format_value(progress))
                    columns = [{'name': v} for v in domain_columns]
                    columns[3].update({'class': 'date'})
                    domain_lines.append({
                        'id': line.id,
                        'parent_id': 'partner_' + str(partner.id),
                        'name': format_date(self.env, line.date),
                        'class': 'date',
                        'columns': columns,
                        'caret_options': caret_type,
                        'level': 4,
                    })

                # load more
                if remaining_lines > 0:
                    domain_lines.append({
                        'id': 'loadmore_%s' % partner.id,
                        'offset': offset + self.MAX_LINES,
                        'progress': progress,
                        'class': 'o_account_reports_load_more text-center',
                        'parent_id': 'partner_%s' % partner.id,
                        'name': _('Load more... (%s remaining)') % remaining_lines,
                        'colspan': 10 if self.user_has_groups('base.group_multi_currency') else 9,
                        'columns': [{}],
                    })
                lines += domain_lines

        if not line_id:
            total_columns = ['', '', '', '', '', self.format_value(total_initial_balance), self.format_value(total_debit), self.format_value(total_credit)]
            if self.user_has_groups('base.group_multi_currency'):
                total_columns.append('')
            total_columns.append(self.format_value(total_balance))
            lines.append({
                'id': 'grouped_partners_total',
                'name': _('Total'),
                'level': 0,
                'class': 'o_account_reports_domain_total',
                'columns': [{'name': v} for v in total_columns],
            })
        return lines

    @api.model
    def _get_report_name(self):
        return _('Partner Ledger')
