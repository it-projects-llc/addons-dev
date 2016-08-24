# -*- coding: utf-8 -*-
from openerp import fields, models
import openerp.addons.decimal_precision as dp


class InstallmentDate(models.Model):
    _name = 'fleet_booking.installment_date'
    _order = 'installment_date'

    installment_date = fields.Date('Date')
    amount = fields.Float(string='Amount', digits_compute=dp.get_precision('Product Price'), default=0)
