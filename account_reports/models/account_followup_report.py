# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.tools.misc import formatLang, format_date
from odoo.tools.translate import _
from odoo.tools import append_content_to_html, DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError

class AccountReportFollowupManager(models.Model):
    _inherit = 'account.report.manager'

    partner_id = fields.Many2one('res.partner')

class AccountFollowupReport(models.AbstractModel):
    _name = "account.followup.report"
    _description = "Follow-up Report"
    _inherit = 'account.report'

    filter_partner_id = False

    def _get_columns_name(self, options):
        """
        Override
        Return the name of the columns of the follow-ups report
        """
        headers = [{},
                   {'name': _('Date'), 'class': 'date', 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Due Date'), 'class': 'date', 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Source Document'), 'style': 'text-align:center; white-space:nowrap;'},
                   {'name': _('Communication'), 'style': 'text-align:right; white-space:nowrap;'},
                   {'name': _('Expected Date'), 'class': 'date', 'style': 'white-space:nowrap;'},
                   {'name': _('Excluded'), 'class': 'date', 'style': 'white-space:nowrap;'},
                   {'name': _('Total Due'), 'class': 'number', 'style': 'text-align:right; white-space:nowrap;'}
                  ]
        if self.env.context.get('print_mode'):
            headers = headers[:5] + headers[7:]  # Remove the 'Expected Date' and 'Excluded' columns
        return headers

    def _get_lines(self, options, line_id=None):
        """
        Override
        Compute and return the lines of the columns of the follow-ups report.
        """
        # Get date format for the lang
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        if not partner:
            return []
        lang_code = partner.lang or self.env.user.lang or 'en_US'

        lines = []
        res = {}
        today = fields.Date.today()
        line_num = 0
        for l in partner.unreconciled_aml_ids:
            if l.company_id == self.env.user.company_id:
                if self.env.context.get('print_mode') and l.blocked:
                    continue
                currency = l.currency_id or l.company_id.currency_id
                if currency not in res:
                    res[currency] = []
                res[currency].append(l)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            for aml in aml_recs:
                amount = aml.currency_id and aml.amount_residual_currency or aml.amount_residual
                date_due = format_date(self.env, aml.date_maturity or aml.date, lang_code=lang_code)
                total += not aml.blocked and amount or 0
                is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                is_payment = aml.payment_id
                if is_overdue or is_payment:
                    total_issued += not aml.blocked and amount or 0
                if is_overdue:
                    date_due = {'name': date_due, 'class': 'color-red date', 'style': 'white-space:nowrap;text-align:center;color: red;'}
                if is_payment:
                    date_due = ''
                move_line_name = aml.invoice_id.name or aml.name
                if self.env.context.get('print_mode'):
                    move_line_name = {'name': move_line_name, 'style': 'text-align:right; white-space:normal;'}
                amount = formatLang(self.env, amount, currency_obj=currency)
                line_num += 1
                expected_pay_date = format_date(self.env, aml.expected_pay_date, lang_code=lang_code) if aml.expected_pay_date else ''
                columns = [
                    format_date(self.env, aml.date, lang_code=lang_code),
                    date_due,
                    aml.invoice_id.origin,
                    move_line_name,
                    expected_pay_date + ' ' + (aml.internal_note or ''),
                    {'name': aml.blocked, 'blocked': aml.blocked},
                    amount,
                ]
                if self.env.context.get('print_mode'):
                    columns = columns[:4] + columns[6:]
                lines.append({
                    'id': aml.id,
                    'invoice_id': aml.invoice_id.id,
                    'view_invoice_id': self.env['ir.model.data'].get_object_reference('account', 'invoice_form')[1],
                    'account_move': aml.move_id,
                    'name': aml.move_id.name,
                    'caret_options': 'followup',
                    'move_id': aml.move_id.id,
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'unfoldable': False,
                    'has_invoice': bool(aml.invoice_id),
                    'columns': [type(v) == dict and v or {'name': v} for v in columns],
                })
            total_due = formatLang(self.env, total, currency_obj=currency)
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': 'total',
                'unfoldable': False,
                'level': 0,
                'columns': [{'name': v} for v in [''] * (3 if self.env.context.get('print_mode') else 5) + [total >= 0 and _('Total Due') or '', total_due]],
            })
            if total_issued > 0:
                total_issued = formatLang(self.env, total_issued, currency_obj=currency)
                line_num += 1
                lines.append({
                    'id': line_num,
                    'name': '',
                    'class': 'total',
                    'unfoldable': False,
                    'level': 0,
                    'columns': [{'name': v} for v in [''] * (3 if self.env.context.get('print_mode') else 5) + [_('Total Overdue'), total_issued]],
                })
            # Add an empty line after the total to make a space between two currencies
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': '',
                'unfoldable': False,
                'level': 0,
                'columns': [],
            })
        return lines

    def _get_default_summary(self, options):
        """
        Override
        Return the overdue message of the company as the summary of the report
        """
        partner = self.env['res.partner'].browse(options.get('partner_id'))
        lang = partner.lang or self.env.user.lang or 'en_US'
        return self.env.user.company_id.with_context(lang=lang).overdue_msg or\
            self.env['res.company'].with_context(lang=lang).default_get(['overdue_msg'])['overdue_msg']

    def _get_report_manager(self, options):
        """
        Override
        Compute and return the report manager for the partner_id in options
        """
        domain = [('report_name', '=', 'account.followup.report'), ('partner_id', '=', options.get('partner_id')), ('company_id', '=', self.env.user.company_id.id)]
        existing_manager = self.env['account.report.manager'].search(domain, limit=1)
        if existing_manager and not options.get('keep_summary'):
            existing_manager.write({'summary': self._get_default_summary(options)})
        if not existing_manager:
            existing_manager = self.env['account.report.manager'].create({
                'report_name': 'account.followup.report',
                'company_id': self.env.user.company_id.id,
                'partner_id': options.get('partner_id'),
                'summary': self._get_default_summary(options)})
        return existing_manager

    @api.multi
    def get_html(self, options, line_id=None, additional_context=None):
        """
        Override
        Compute and return the content in HTML of the followup for the partner_id in options
        """
        if additional_context is None:
            additional_context = {}
        partner = self.env['res.partner'].browse(options['partner_id'])
        additional_context['partner'] = partner
        additional_context['lang'] = partner.lang or self.env.user.lang or 'en_US'
        additional_context['invoice_address_id'] = self.env['res.partner'].browse(partner.address_get(['invoice'])['invoice'])
        additional_context['today'] = fields.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT)
        return super(AccountFollowupReport, self).get_html(options, line_id=line_id, additional_context=additional_context)

    def _get_report_name(self):
        """
        Override
        Return the name of the report
        """
        return _('Followup Report')

    def _get_reports_buttons(self):
        """
        Override
        Return an empty list because this report doesn't contain any buttons
        """
        return []

    def _get_templates(self):
        """
        Override
        Return the templates of the report
        """
        templates = super(AccountFollowupReport, self)._get_templates()
        templates['main_template'] = 'account_reports.template_followup_report'
        templates['line_template'] = 'account_reports.line_template_followup_report'
        return templates

    @api.model
    def get_followup_informations(self, partner_id, options):
        """
        Return all informations needed by the view:
        - the report manager id
        - the content in HTML of the report
        - the state of the next_action
        """
        options['partner_id'] = partner_id
        report_manager_id = self._get_report_manager(options).id
        html = self.get_html(options)
        next_action = False
        if not options.get('keep_summary'):
            next_action = self.env['res.partner'].browse(partner_id).get_next_action()
        return {
            'report_manager_id': report_manager_id,
            'html': html,
            'next_action': next_action,
        }

    @api.model
    def send_email(self, options):
        """
        Send by mail the followup to the customer
        """
        partner = self.env['res.partner'].browse(options.get('partner_id'))
        email = self.env['res.partner'].browse(partner.address_get(['invoice'])['invoice']).email
        options['keep_summary'] = True
        if email and email.strip():
            # When printing we need te replace the \n of the summary by <br /> tags
            body_html = self.with_context(print_mode=True, mail=True, lang=partner.lang or self.env.user.lang).get_html(options)
            start_index = body_html.find(b'<span>', body_html.find(b'<div class="o_account_reports_summary">'))
            end_index = start_index > -1 and body_html.find(b'</span>', start_index) or -1
            if end_index > -1:
                replaced_msg = body_html[start_index:end_index].replace(b'\n', b'<br />')
                body_html = body_html[:start_index] + replaced_msg + body_html[end_index:]
            msg = _('Follow-up email sent to %s') % email
            msg += '<br>' + body_html.decode('utf-8')
            msg_id = partner.message_post(body=msg)
            email = self.env['mail.mail'].create({
                'mail_message_id': msg_id.id,
                'subject': _('%s Payment Reminder') % (self.env.user.company_id.name) + ' - ' + partner.name,
                'body_html': append_content_to_html(body_html, self.env.user.signature or '', plaintext=False),
                'email_from': self.env.user.email or '',
                'email_to': email,
                'body': msg,
            })
            partner.message_subscribe([partner.id])
            return True
        raise UserError(_('Could not send mail to partner because it does not have any email address defined'))

    @api.model
    def print_followups(self, records):
        """
        Print one or more followups in one PDF
        records contains either a list of records (come from an server.action) or a field 'ids' which contains a list of one id (come from JS)
        """
        res_ids = records['ids'] if 'ids' in records else records.ids  # records come from either JS or server.action
        self.env['res.partner'].browse(res_ids).message_post(body=_('Follow-up letter printed'))
        return self.env.ref('account_reports.action_report_followup').report_action(res_ids)

    def _execute_followup_partner(self, partner):
        """
        If the customer is in_need_of_action, we have to send email, print letter and mark as done
        Return partner if it's necessary to print
        """
        if partner.followup_status == 'in_need_of_action':
            partner.send_followup_email()
            next_date = fields.datetime.now() + timedelta(days=self.env.user.company_id.days_between_two_followups)
            partner.update_next_action(options={'next_action_date': datetime.strftime(next_date, DEFAULT_SERVER_DATE_FORMAT), 'next_action_type': 'auto'})
            return partner
        return None

    @api.model
    def execute_followup(self, records):
        """
        Execute the actions to do with followups.
        """
        to_print = []
        for partner in records:
            partner_tmp = self._execute_followup_partner(partner)
            if partner_tmp:
                to_print.append(partner_tmp.id)
        if not to_print:
            return
        return self.print_followups(self.env['res.partner'].browse(to_print))
