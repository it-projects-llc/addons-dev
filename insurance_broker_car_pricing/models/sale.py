# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class SaleOrder(models.Model):
    _inherit = "sale.order"

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['vehicle_id'] = self.vehicle_id.id
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'start_date': self.start_date,
            'end_date': self.end_date,
            'vehicle_id': self.vehicle_id.id,
        })
        return res

    @api.model
    def default_get(self, fields_list):
        result = super(SaleOrderLine, self).default_get(fields_list)
        order_id = self._context.get('sale_order_id')
        if order_id:
            order = self.env['sale.order'].browse(order_id)
            result['vehicle_id'] = order.vehicle_id.id
            vehicle = self.env['fleet.vehicle'].browse(order.vehicle_id.id)
            if vehicle:
                result['product_id'] = vehicle.product_id.id
        result['start_date'] = (date.today() + timedelta(1)).strftime(DF)
        result['end_date'] = (date.today() + relativedelta(years=1)).strftime(DF)
        result['uom_id'] = self.env.ref('insurance_broker_car_pricing.product_uom_year').id

        return result

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id.product_id:
            self.product_id = self.vehicle_id.product_id

    @api.model
    def create(self, vals):
        if not vals.get('start_date') and not vals.get('end_date'):
            vals['start_date'] = date.today() + timedelta(1)
            vals['end_date'] = date.today() + relativedelta(years=1)
            vals['product_uom'] = self.env.ref('insurance_broker_car_pricing.product_uom_year').id
        soline = super(SaleOrderLine, self).create(vals)
        return soline

    @api.multi
    def write(self, vals):
        if not vals.get('start_date') and not vals.get('end_date'):
            vals['start_date'] = date.today() + timedelta(1)
            vals['end_date'] = date.today() + relativedelta(years=1)
            vals['product_uom'] = self.env.ref('insurance_broker_car_pricing.product_uom_year').id
        return super(SaleOrderLine, self).write(vals)

    @api.one
    @api.constrains('start_date', 'end_date')
    def _check_start_end_dates(self):
        super(SaleOrderLine, self)._check_start_end_dates()
        if self.start_date and datetime.strptime(self.start_date, DF).date() < datetime.now().date():
            raise ValidationError(_(
                "Start Date shouldn't be earlier than today for sale order line with "
                "Product '%s'.") % (self.product_id.name))
        if self.end_date and datetime.strptime(self.end_date, DF).date() < datetime.now().date():
            raise ValidationError(_(
                "End Date shouldn't be earlier than today for sale order line with "
                "Product '%s'.") % (self.product_id.name))
        if self.start_date and self.end_date:
            start_date = datetime.strptime(self.start_date, DF).date()
            end_date = datetime.strptime(self.end_date, DF).date() + timedelta(1)
            reference_date = start_date + relativedelta(years=1)
            if end_date - start_date > reference_date - start_date:
                raise ValidationError(_(
                    "Time period should be less than 1year/12months for sale order line with "
                    "Product '%s'.") % (self.product_id.name))

    @api.onchange('end_date', 'start_date')
    def _onchange_dates(self):
        if self.start_date and self.end_date:
            start_date = datetime.strptime(self.start_date, DF).date()
            end_date = datetime.strptime(self.end_date, DF).date() + timedelta(1)
            reference_date = start_date + relativedelta(years=1)
            if end_date - start_date < reference_date - start_date:
                months = relativedelta(end_date, start_date).months
                self.product_uom_qty = months
                self.product_uom = self.env.ref('insurance_broker_car_pricing.product_uom_month').id
            elif end_date - start_date >= reference_date - start_date:
                self.product_uom_qty = 1
                self.product_uom = self.env.ref('insurance_broker_car_pricing.product_uom_year').id
