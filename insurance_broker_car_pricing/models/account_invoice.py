# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')

    @api.model
    def default_get(self, fields_list):
        result = super(AccountInvoiceLine, self).default_get(fields_list)
        invoice_id = self._context.get('default_invoice_id')
        if invoice_id:
            invoice = self.env['account.invoice'].browse(invoice_id)
            result['vehicle_id'] = invoice.vehicle_id.id
            vehicle = self.env['fleet.vehicle'].browse(invoice.vehicle_id.id)
            if vehicle:
                result['product_id'] = vehicle.product_id.id

        return result

    @api.multi
    @api.constrains('start_date', 'end_date')
    def _check_start_end_dates(self):
        super(AccountInvoiceLine, self)._check_start_end_dates()
        for invline in self:
            if invline.start_date and datetime.strptime(invline.start_date, DF).date() < datetime.now().date():
                raise ValidationError(
                    _("Start Date shouldn't be less than today for invoice line with "
                        "Description '%s'.")
                    % (invline.name))
            if invline.end_date and datetime.strptime(invline.end_date, DF).date() < datetime.now().date():
                raise ValidationError(
                    _("End Date shouldn't be less than today for invoice line with "
                        "Description '%s'.")
                    % (invline.name))
            if invline.start_date and invline.end_date:
                start_date = datetime.strptime(invline.start_date, DF).date()
                end_date = datetime.strptime(invline.end_date, DF).date() + timedelta(1)
                reference_date = start_date + relativedelta(years=1)
                if end_date - start_date > reference_date - start_date:
                    raise ValidationError(
                        _("Time period should be less than 1year/12months for invoice line with "
                            "Description '%s'.")
                        % (invline.name))

    @api.model
    def create(self, vals):
        if not vals.get('start_date') and not vals.get('end_date'):
            vals['start_date'] = date.today() + timedelta(1)
            vals['end_date'] = date.today() + relativedelta(years=1)
            vals['uom_id'] = self.env.ref('insurance_broker_car_pricing.product_uom_year').id
        invline = super(AccountInvoiceLine, self).create(vals)
        return invline

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id.product_id:
            self.product_id = self.vehicle_id.product_id

    @api.onchange('end_date', 'start_date')
    def _onchange_dates(self):
        if self.start_date and self.end_date:
            start_date = datetime.strptime(self.start_date, DF).date()
            end_date = datetime.strptime(self.end_date, DF).date() + timedelta(1)
            reference_date = start_date + relativedelta(years=1)
            if end_date - start_date < reference_date - start_date:
                months = relativedelta(end_date, start_date).months
                self.quantity = months
                self.uom_id = self.env.ref('insurance_broker_car_pricing.product_uom_month').id
            elif end_date - start_date >= reference_date - start_date:
                self.quantity = 1
                self.uom_id = self.env.ref('insurance_broker_car_pricing.product_uom_year').id
