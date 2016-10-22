#-*- coding:utf-8 -*-
##############################################################################
#
#    Payroll Senegal
#    Copyright (C) 2013-TODAY Ergobit Consulting (<http://ergobit.org>).
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

{
    'name': 'Payroll - SN',
    'summary': 'Senegal localization for Payroll application',
    'version': '1.0',
    'category': 'Localization',

    'author': 'ERGOBIT Consulting, IT-Projects LLC',
    'website': 'http://www.ergobit.org',
    'images': [
        'images/hr_company_contributions.jpeg',
        'images/hr_salary_heads.jpeg',
        'images/hr_salary_structure.jpeg',
        'images/hr_employee_payslip.jpeg'
    ],
    'depends': [
        'account',
        'hr_payroll',
        'hr_holidays_legal_leave',
        'hr_holidays_compute_days',
    ],
    'data': [
        'views/l10n_syscoa_payroll_view.xml',
        'l10n_syscoa_payroll_report.xml',

        'data/l10n_syscoa_account_data.xml',
        'data/l10n_syscoa_contract_data.xml',
        'data/l10n_syscoa_payroll_data.xml',

        'report/syscoa_report_payslip.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
