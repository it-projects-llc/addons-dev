# coding: utf-8
from odoo import api, fields, models, _


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def load_for_current_company(self, sale_tax_rate, purchase_tax_rate):
        res = super(AccountChartTemplate, self).load_for_current_company(sale_tax_rate, purchase_tax_rate)

        # by default, anglo-saxon companies should have totals
        # displayed below sections in their reports
        company = self.env.user.company_id
        company.totals_below_sections = company.anglo_saxon_accounting

        return res
