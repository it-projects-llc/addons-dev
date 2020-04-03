# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from odoo import api, fields, models, _
from odoo.tools.misc import format_date

_FOLLOWUP_STATUS = [('in_need_of_action', 'In need of action'), ('with_overdue_invoices', 'With overdue invoices'), ('no_action_needed', 'No action needed')]

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    payment_next_action_date = fields.Date('Next Action Date', copy=False, company_dependent=True,
                                           help="The date before which no action should be taken.")
    unreconciled_aml_ids = fields.One2many('account.move.line', 'partner_id',
                                           domain=[('reconciled', '=', False),
                                                   ('account_id.deprecated', '=', False),
                                                   ('account_id.internal_type', '=', 'receivable')])
    partner_ledger_label = fields.Char(compute='_compute_partner_ledger_label')
    total_due = fields.Monetary(compute='_compute_for_followup', store=False, readonly=True)
    total_overdue = fields.Monetary(compute='_compute_for_followup', store=False, readonly=True)
    followup_status = fields.Selection(
        _FOLLOWUP_STATUS,
        compute='_compute_for_followup',
        store=False,
        string='Followup status',
        search='_search_status')

    def _search_status(self, operator, value):
        """
        Compute the search on the field 'followup_status'
        """
        if operator != '=' or value not in ['in_need_of_action', 'with_overdue_invoices', 'no_action_needed']:
            return []

        today = fields.Date.context_today(self)
        domain = self.get_followup_lines_domain(today, overdue_only=value == 'with_overdue_invoices')

        query = self.env['account.move.line']._where_calc(domain)
        tables, where_clause, where_params = query.get_sql()
        sql = """SELECT "account_move_line".partner_id
                 FROM %s
                 WHERE %s
                   AND "account_move_line".partner_id IS NOT NULL
                 GROUP BY "account_move_line".partner_id"""
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        if value in ('in_need_of_action', 'with_overdue_invoices'):
            return [('id', 'in', results)]
        return [('id', 'not in', results)]

    def _compute_for_followup(self):
        """
        Compute the fields 'total_due', 'total_overdue' and 'followup_status'
        """
        partners_in_need_of_action = self._get_partners_in_need_of_action().ids
        for record in self:
            total_due = 0
            total_overdue = 0
            followup_status = "no_action_needed"
            today = fields.Date.today()
            for aml in record.unreconciled_aml_ids:
                if aml.company_id == self.env.user.company_id:
                    amount = aml.amount_residual
                    total_due += amount
                    is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                    if is_overdue:
                        total_overdue += not aml.blocked and amount or 0
            if total_overdue > 0:
                followup_status = "in_need_of_action" if record.id in partners_in_need_of_action else "with_overdue_invoices"
            else:
                followup_status = "no_action_needed"
            record.total_due = total_due
            record.total_overdue = total_overdue
            record.followup_status = followup_status

    @api.depends('supplier', 'customer')
    def _compute_partner_ledger_label(self):
        for record in self:
            if record.supplier == record.customer:
                record.partner_ledger_label = _('Partner Ledger')
            elif record.supplier:
                record.partner_ledger_label = _('Vendor Ledger')
            else:
                record.partner_ledger_label = _('Customer Ledger')

    def _get_partners_in_need_of_action(self, overdue_only=False):
        """
        Return a list of partners which are in status 'in_need_of_action'.
        If 'overdue_only' is set to True, partners in status 'with_overdue_invoices' are included in the list
        """
        today = fields.Date.context_today(self)
        domain = self.get_followup_lines_domain(today, overdue_only=overdue_only, only_unblocked=True)
        query = self.env['account.move.line']._where_calc(domain)
        tables, where_clause, where_params = query.get_sql()
        sql = """SELECT "account_move_line".partner_id
                 FROM %s
                 WHERE %s
                   AND "account_move_line".partner_id IS NOT NULL
                 GROUP BY "account_move_line".partner_id"""
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        result = self.env.cr.fetchall()
        return self.browse(result[0] if result else [])

    def _get_needofaction_fup_lines_domain(self, date):
        # that part of the domain concerns the date filtering and is overwritten in account_reports_followup
        overdue_domain = ['|', '&', ('date_maturity', '!=', False), ('date_maturity', '<', date), '&', ('date_maturity', '=', False), ('date', '<', date)]
        return overdue_domain + ['|', ('next_action_date', '=', False), ('next_action_date', '<=', date)]

    def get_followup_lines_domain(self, date, overdue_only=False, only_unblocked=False):
        """ returns the domain to use on account.move.line to get the partners 'in need of action' or 'with overdue invoices'.
        This is used by the followup_status computed field"""
        domain = super(ResPartner, self).get_followup_lines_domain(date, overdue_only=overdue_only, only_unblocked=only_unblocked)
        if not overdue_only:
            domain += self._get_needofaction_fup_lines_domain(date)
        return domain

    def get_next_action(self):
        """
        Compute the next action status of the customer. It can be 'manual' or 'auto'.
        """
        self.ensure_one()
        lang_code = self.lang or self.env.user.lang or 'en_US'
        date_auto = format_date(self.env, fields.datetime.now() + timedelta(days=self.env.user.company_id.days_between_two_followups), lang_code=lang_code)
        if self.payment_next_action_date:
            return {
                'type': 'manual',
                'date': self.payment_next_action_date,
                'date_auto': date_auto
            }
        return {
            'type': 'auto',
            'date_auto': date_auto
        }

    @api.multi
    def change_expected_date(self, options=False):
        if not options or 'expected_pay_date' not in options or 'move_line_id' not in options:
            return True
        for record in self:
            aml = self.env['account.move.line'].search([('id', '=', int(options['move_line_id']))], limit=1)
            old_date = aml.expected_pay_date
            aml.write({'expected_pay_date': options['expected_pay_date']})
            msg = _('Expected pay date has been changed from %s to %s for invoice %s') % (old_date or _('any'), aml.expected_pay_date, aml.invoice_id.number)
            record.message_post(body=msg)
        return True

    @api.multi
    def change_next_action(self, date):
        for record in self:
            msg = _('Next action date: ') + date
            record.message_post(body=msg)
        return True

    def update_next_action(self, options=False):
        """Updates the next_action_date of the right account move lines"""
        if not options or 'next_action_date' not in options or 'next_action_type' not in options:
            return
        next_action_date = options['next_action_date'][0:10]
        today = fields.datetime.now()
        domain = self.get_followup_lines_domain(today)
        aml = self.env['account.move.line'].search(domain)
        aml.write({'next_action_date': next_action_date})
        self.write({'payment_next_action_date': next_action_date})
        if options['next_action_type'] == 'manual':
            self.change_next_action(options['next_action_date'])

    def open_action_followup(self):
        self.ensure_one()
        return {
            'name': _("Overdue Payments for %s") % self.display_name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [[self.env.ref('account_reports.customer_statements_form_view').id, 'form']],
            'res_model': 'res.partner',
            'res_id': self.id,
        }

    def open_partner_ledger(self):
        return {
            'type': 'ir.actions.client',
            'name': _('Partner Ledger'),
            'tag': 'account_report',
            'options': {'partner_ids': [self.id]},
            'ignore_session': 'both',
            'context': "{'model':'account.partner.ledger'}"
        }

    def send_followup_email(self):
        """
        Send a follow-up report by email to customers in self
        """
        for record in self:
            options = {
                'partner_id': record.id,
            }
            self.env['account.followup.report'].send_email(options)

    def get_followup_html(self):
        """
        Return the content of the follow-up report in HTML
        """
        options = {
            'partner_id': self.id,
            'keep_summary': True
        }
        return self.env['account.followup.report'].with_context(print_mode=True, lang=self.lang or self.env.user.lang).get_html(options)
