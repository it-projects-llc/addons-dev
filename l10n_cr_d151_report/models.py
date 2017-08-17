# coding: utf-8
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx


class D151Xlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, partners):
        if data['show_details']:
            self.render_detailed_report(workbook, data)
        else:
            self.render_report(workbook, data)

    @staticmethod
    def render_report(workbook, data):
        filtered_data = data['filtered_data']
        # formatting
        category = workbook.add_format({'bold': True})
        partner_cell = workbook.add_format({'bold': True})
        category.set_bg_color('silver')
        cell = workbook.add_format()
        cell.set_font_size('10')
        partner_cell.set_font_size('10')
        sheet = workbook.add_worksheet()

        column = 0
        for item in sorted(filtered_data, key=lambda k: k['cr_d151_category_code']):
            name = '%s - %s' % (item['cr_d151_category_code'], item['cr_d151_category_name'])
            sheet.write(column, 0, name, category)
            for i in range(1,2):
                sheet.write(column, i, '', category)
            sheet.write(column, 2, item['category_amount'], category)
            column += 1
            for partner in sorted(item['partners'], key=lambda k: k['partner']):
                sheet.write(column, 0, partner['partner'], partner_cell)
                sheet.write(column, 1, partner['ref'], partner_cell)
                sheet.write(column, 2, partner['partner_amount'], partner_cell)
                column += 1

    @staticmethod
    def render_detailed_report(workbook, data):
        filtered_data = data['filtered_data']
        # formatting
        category = workbook.add_format({'bold': True})
        partner_cell = workbook.add_format({'bold': True})
        category.set_bg_color('silver')
        cell = workbook.add_format()
        cell.set_font_size('10')
        partner_cell.set_font_size('10')
        sheet = workbook.add_worksheet()
        column = 0
        for item in sorted(filtered_data, key=lambda k: k['cr_d151_category_code']):
            name = '%s - %s' % (item['cr_d151_category_code'], item['cr_d151_category_name'])
            sheet.write(column, 0, name, category)
            for i in range(1, 5):
                sheet.write(column, i, '', category)
            sheet.write(column, 5, item['category_amount'], category)

            column += 1
            for partner in sorted(item['partners'], key=lambda k: k['partner']):
                sheet.write(column, 0, partner['partner'], partner_cell)
                sheet.write(column, 1, partner['ref'], partner_cell)
                sheet.write(column, 5, partner['partner_amount'], partner_cell)
                column += 1
                # labels block
                if data['show_details']:
                    sheet.write(column, 0, 'Date', partner_cell)
                    sheet.write(column, 1, 'Move', partner_cell)
                    sheet.write(column, 2, 'Reference', partner_cell)
                    sheet.write(column, 3, 'Account', partner_cell)
                    sheet.write(column, 4, 'Journal', partner_cell)
                    sheet.write(column, 5, 'Amount', partner_cell)
                    column += 1
                    # aml info block
                    for aml in partner['amls']:
                        sheet.write(column, 0, aml['date'], cell)
                        sheet.write(column, 1, aml['move'], cell)
                        sheet.write(column, 2, aml['reference'], cell)
                        sheet.write(column, 3, aml['account'], cell)
                        sheet.write(column, 4, aml['journal'], cell)
                        sheet.write(column, 5, aml['amount'], cell)
                        column += 1


D151Xlsx(
    'report.l10n_cr_d151_report.d151_report_template',
    'account.cr.d151.category')
