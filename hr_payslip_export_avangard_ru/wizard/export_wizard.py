# -*- coding: utf-8 -*-
from openerp import api, fields, models
import xlwt
import tempfile
import os

class ExportPayslips(models.TransientModel):
    _name = "hr.payslip.export.excel"
    _description = "Export payslips in excel"
    line_ids = fields.Many2many('hr.payslip')

    @api.multi
    def method_in_model(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        font0 = xlwt.Font()
        font0.name = 'Times New Roman'
        font0.bold = True
        style0 = xlwt.XFStyle()
        style0.font = font0
        style1 = xlwt.XFStyle()
        style1.num_format_str = 'DD-MM-YYYY'
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Report')
        ws.col(0).width = 10000
        ws.col(1).width = 5000
        ws.col(2).width = 7000
        ws.col(3).width = 5000
        str_num = 0
        ws.write(str_num, 0, 'Name', style0)
        ws.write(str_num, 1, 'Birthday', style0)
        ws.write(str_num, 2, 'Acc number', style0)
        ws.write(str_num, 3, 'Net amount', style0)
        str_num += 1
        for record in self.env['hr.payslip'].browse(active_ids):
            if not record.net:
                continue
            empl_name = record.employee_id.name
            empl_birthday = record.employee_id.birthday
            empl_acc_number = record.employee_id.bank_account_id.acc_number
            net_sum = record.net

            ws.write(str_num, 0, empl_name, style1)
            ws.write(str_num, 1, empl_birthday, style1)
            ws.write(str_num, 2, empl_acc_number, style1)
            ws.write(str_num, 3, net_sum,style0)
            str_num += 1

        file = tempfile.NamedTemporaryFile()
        wb.save(file.name)
        os.system('libreoffice ' + file.name)
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def default_get(self, fields):
        res = super(ExportPayslips, self).default_get(fields)
        record_ids = self.env.context.get('active_ids')
        res.update({'line_ids': [(6, 0, record_ids)]})
        return res

