#-*- coding:utf-8 -*-

##############################################################################
#
#    ErgoBIT Payroll Senegal
#    Copyright (C) 2013-TODAY ErgoBIT Consulting (<http://ergobit.org>).
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from dateutil import parser
from dateutil import relativedelta
from openerp import models
from openerp.report import report_sxw
from datetime import date
import odoo

import locale


def formatl(n, digits=None):
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')  # "de_DE.UTF-8" do it with dots
    if digits is None:
        return locale.format('%d', n, True)
    else:
        return locale.currency(n, False)


class ErgobitPayslipReport(report_sxw.rml_parse):

    # Define constants for salary categories
    # ---------------------------------------
    C_BASIC = 'BASIC'
    C_ALW = 'ALW'
    C_RED = 'RED'
    C_NATU = 'NATU'
    C_GROSS = 'GROSS'
    C_DED = 'DED'
    C_TAX = 'TAX'
    C_TAXX = 'TAXX'
    C_ALWN = 'ALWN'
    C_NET = 'NET'

    C_AVCE = 'AVCE'
    C_PAYB = 'PAYB'
    C_SYN = 'SYN'
    C_RETN = 'RETN'

    C_COMP = 'COMP'  # Retenue patronale (-)
    C_COMPP = 'COMPP'  # Retenue patronale (+)

    C_TOTM = 'TOTM'
    C_TOTA = 'TOTA'


# Constants for some rule codes
#---------------------------------------
    C_R500 = '500'        # rule code for I/R
    C_R550 = '550'        # rule code for TRIMF

# Dict objects containing total values
    total_m = {}
    total_y = {}

    def __init__(self, cr, uid, name, context):
        super(ErgobitPayslipReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_payslip_lines_main': self.get_payslip_lines_main,
            'get_payslip_lines_total': self.get_payslip_lines_total,
            'get_total': self.get_total,
            'get_quantity': self.get_quantity,
            'get_amount_base': self.get_amount_base,
            'get_rate_salarial': self.get_rate_salarial,
            'get_gain_salarial': self.get_gain_salarial,
            'get_deduction_salarial': self.get_deduction_salarial,
            'get_rate_patronal': self.get_rate_patronal,
            'get_contribution_patronal_plus': self.get_contribution_patronal_plus,
            'get_contribution_patronal': self.get_contribution_patronal,
            'parse': self.parse,
            'get_years': self.get_years,
            'get_months': self.get_months,
            'get_worked_hours': self.get_worked_hours,
        })

    def parse(self, my_date):
        d, m, y = map(int, my_date.split('/'))
        return date(y, m, d)

    def get_months(self, date_1):
        month = {}
        date_1 = datetime.strptime(str(date_1), '%Y-%m-%d')
        date_1 = datetime.strptime(str(str(date.today().year - 1) + '-' + str(date_1.month) + '-' + str(date_1.day)), '%Y-%m-%d')
        date_2 = datetime.strptime(str(date.today()), '%Y-%m-%d')
        month = relativedelta.relativedelta(date_2, date_1).months
        return month

    def get_years(self, date_1):
        year = {}
        date_1 = datetime.strptime(str(date_1), '%Y-%m-%d')
        date_2 = datetime.strptime(str(date.today()), '%Y-%m-%d')
        year = relativedelta.relativedelta(date_2, date_1).years
        return year

    def get_payslip_lines_main(self, lines_ids):
        """ Read the lines for the central table excluding
                - company contribution *_COMP
                - Column totals
                - yearly totals
        """
        env = odoo.api.Environment(self.cr, self.uid, {})
        category_ids = env['hr.salary.rule.category'].search(
            [('code', 'not in', [self.C_COMP, self.C_COMPP, self.C_NET, self.C_TOTA, self.C_TOTM])])

        payslip_line = env['hr.payslip.line']
        res = []
        ids = []

        for idx in range(len(lines_ids)):
            if (lines_ids[idx].appears_on_payslip is True) and (int(lines_ids[idx].category_id) in category_ids):
                ids.append(lines_ids[idx].id)
        if ids:
            res = payslip_line.browse(ids)
        return res

    def get_quantity(self, psline):
        if round(float(psline.quantity), 2) == 1.00 or round(float(psline.quantity), 2) == 0.00:
            return ''
#        return report_sxw.rml_parse.formatLang(self, psline.quantity)
        return formatl(psline.quantity, 2)

    def get_amount_base(self, psline):
        env = odoo.api.Environment(self.cr, self.uid, {})

        if round(float(psline.amount), 2) == 0.00:  # '{0:.}'.format(amount)
            return ''
        # no base for I/R, TRIMF
        if psline.code in [self.C_R500, self.C_R550]:
            return ''
        # Only basic, ded and alwn
        category_ids = env['hr.salary.rule.category'].search(
            [('code', 'in', [self.C_BASIC, self.C_DED, self.C_TAX, self.C_TAXX, self.C_ALWN, self.C_ALW])])
        if int(psline.category_id) in category_ids:
            if psline.category_id.code in [self.C_ALW, self.C_BASIC]:
                if psline.code in ['100', '210', '220', '230', '240']:
                    if round(float(psline.amount), 2) == 0.00:
                        return ''
                    return formatl(psline.amount, 2)
            else:
                if round(float(psline.amount), 2) == 0.00:
                    return ''
                return formatl(psline.amount)
        return ''

    def get_rate_salarial(self, psline):
        if round(float(psline.rate), 2) == 100.00 or round(float(psline.rate), 2) == 0.00:
            return ''
        return formatl(psline.rate, 2)

    def get_worked_hours(self, slip, code='WORK100'):
        return formatl(slip.get_worked_hours(code), 2)

    def get_gain_salarial(self, psline):
        env = odoo.api.Environment(self.cr, self.uid, {})
        if round(float(psline.total), 2) == 0.00:
            return ''
        category_ids = env['hr.salary.rule.category'].search([('code', 'in', [self.C_RED, self.C_DED, self.C_TAX, self.C_PAYB, self.C_SYN, self.C_RETN])])
        if int(psline.category_id) in category_ids:
            return ''
        if psline.code == '100':
            if psline.slip_id.contract_id.time_mod == 'fixed' and \
                    psline.slip_id.contract_id.time_fixed == psline.slip_id.get_worked_hours('WORKED') and \
                    psline.slip_id.get_worked_hours('WORK100') == psline.slip_id.get_worked_hours('WORKED'):
                return formatl(psline.slip_id.contract_id.wage)
            else:
                return formatl(round(float(psline.total)))
#                return formatl(math.ceil(float(psline.total)))
        return formatl(psline.total)

    def get_deduction_salarial(self, psline):
        env = odoo.api.Environment(self.cr, self.uid, {})
        if round(float(psline.total), 2) == 0.00:
            tax_cat_ids = env['hr.salary.rule.category'].search([('code', 'in', [self.C_TAX])])
            if int(psline.category_id) in tax_cat_ids:  # for tax return 0 instead of ''
                return 0
            return ''
        category_ids = env['hr.salary.rule.category'].search([('code', 'in', [self.C_RED, self.C_DED, self.C_TAX, self.C_PAYB, self.C_SYN, self.C_RETN])])
        if int(psline.category_id) in category_ids:
            return formatl(psline.total)
        return ''

    def get_rate_patronal(self, psline):
        env = odoo.api.Environment(self.cr, self.uid, {})
        psline_code_comp = psline.code + '_C'
        pooler = env['hr.payslip.line']
        payslip_line_comp_id = pooler.search([('slip_id', '=', psline.slip_id.id), ('code', '=', psline_code_comp)])
        payslip_line_comp = pooler.browse(payslip_line_comp_id)
        if payslip_line_comp:
            rate = payslip_line_comp[0].rate
            if round(float(rate), 2) == 100.00:
                return ''
            return formatl(rate, 2)
        return ''

    def get_contribution_patronal_plus(self, psline):
        env = odoo.api.Environment(self.cr, self.uid, {})
        psline_code_compp = psline.code + '_CP'
        pooler = env['hr.payslip.line']
        payslip_line_compp_id = pooler.search([('slip_id', '=', psline.slip_id.id), ('code', '=', psline_code_compp)])
        payslip_line_compp = pooler.browse(payslip_line_compp_id)
        if payslip_line_compp:
            total = payslip_line_compp[0].total
            if round(float(total), 2) == 0.00:
                return ''
            return formatl(total)
        return ''

    def get_contribution_patronal(self, psline):
        env = odoo.api.Environment(self.cr, self.uid, {})
        psline_code_comp = psline.code + '_C'
        pooler = env['hr.payslip.line']
        payslip_line_comp_id = pooler.search([('slip_id', '=', psline.slip_id.id), ('code', '=', psline_code_comp)])
        payslip_line_comp = pooler.browse(payslip_line_comp_id)
        if payslip_line_comp:
            total = payslip_line_comp[0].total
            if round(float(total), 2) == 0.00:
                return ''
            return formatl(total)
        return ''

    def get_payslip_lines_total(self, lines_ids, timeref='MONTH'):
        """
        Read the monthly and the yearly sum lines for the bottom table and
             save them in a dict object according to timeref MONTH or YEAR
        Returns a pseudo dict object {(PSEUDO, '')}
        """
        env = odoo.api.Environment(self.cr, self.uid, {})
        payslip_line = env['hr.payslip.line']

        if timeref == 'MONTH':
            res = dict.fromkeys(['1100', '1200', '1300', '1400', '1500', 'B100', '1600', '1700', '1000', '1020'], 0.00)
            category_ids = env['hr.salary.rule.category'].search([('code', 'in', [self.C_TOTM, self.C_NET])])
        else:
            res = dict.fromkeys(['2100', '2200', '2300', '2400', '2500', '2600', '2700', '2000', '2020'], 0.00)
            category_ids = env['hr.salary.rule.category'].search([('code', '=', self.C_TOTA)])

        ids = []
        for idx in range(len(lines_ids)):
            if (lines_ids[idx].appears_on_payslip is True) and (int(lines_ids[idx].category_id) in category_ids):
                ids.append(lines_ids[idx].id)
        if ids:
            payslip_line_total = payslip_line.browse(ids)
            if payslip_line_total:
                for linx in range(len(payslip_line_total)):
                    if payslip_line_total[linx].code in res.keys():
                        d = dict.fromkeys([payslip_line_total[linx].code], payslip_line_total[linx].total)
                        res.update(d)

        if timeref == 'MONTH':
            self.total_m = res
        else:
            self.total_y = res

        return dict.fromkeys(['PSEUDO'], '')

    def get_total(self, timeref, key, lines_ids=None):
        if len(self.total_m) == 0 and bool(lines_ids):
            self.get_payslip_lines_total(lines_ids, 'MONTH')
        if len(self.total_y) == 0 and bool(lines_ids):
            self.get_payslip_lines_total(lines_ids, 'YEAR')

        total = (self.total_y if timeref == 'YEAR' else self.total_m)
        res = total.get(key, '')
        if res == '':
            return ''
        if round(float(res), 2) == 0.00:
            return ''
        if key in ['B100', '1500', '1600', '2500', '2600']:
            return formatl(res, 2)
        else:
            return formatl(res)


class WrappedErgobitReportPayslip(models.AbstractModel):
    _name = 'report.l10n_syscoa_payroll.syscoa_report_payslip'
    _inherit = 'report.abstract_report'
    _template = 'l10n_syscoa_payroll.syscoa_report_payslip'
    _wrapped_report_class = ErgobitPayslipReport

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
