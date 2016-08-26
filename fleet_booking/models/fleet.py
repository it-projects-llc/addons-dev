# -*- coding: utf-8 -*-
from openerp import api, fields, models


class Vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    _inherits = {'fleet_rental.document': 'document_id'}
    document_id = fields.Many2one('fleet_rental.document',
                                  required=True, ondelete='restrict', auto_join=True)
    asset_id = fields.Many2one('account.asset.asset', ondelete='restrict', readonly=True)
    product_id = fields.Many2one('product.product', 'Vehicle Product', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Vendor',
                                 default=lambda self: self.env.ref('fleet_booking.res_partner_vehicle_vendor').id)
    model_year = fields.Date('Model Year')
    paid = fields.Float('Paid amount')
    remain = fields.Float('Remaining amount')
    reg_expiry = fields.Date('Registration expiry')
    ins_expiry = fields.Date('Insurance expiry')
    next_maintain = fields.Date('Next maintenance')
    payments_ids = fields.One2many('account.invoice', 'fleet_vehicle_id', string='Payments')
    total_documents = fields.Integer(compute='_count_total_documents', string="Total documents", default=0)
    depreciation_ids = fields.One2many(related='asset_id.depreciation_line_ids')
    state_id = fields.Many2one('fleet.vehicle.state', readonly=True, ondelete="restrict",
                               default=lambda self: self.env.ref('fleet_rental_document.vehicle_state_active').id)
    lease_installment_date_ids = fields.Many2many('fleet_booking.installment_date',
                                                  'fleet_booking_lease_dates_rel')
    insurance_installment_date_ids = fields.Many2many('fleet_booking.installment_date',
                                                      'fleet_booking_insurance_dates_rel')
    account_asset_id = fields.Many2one('account.account', string='Accumulated Depreciation Account',
                                       domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    account_depreciation_id = fields.Many2one('account.account', string='Depreciation Expense Account',
                                              domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])

    @api.multi
    def _count_total_documents(self):
        pass
        # for rec in self:
        #     docs_ids = self.env['fleet_rental.document'].search([('vehicle_id.id', '=', rec.id)])
        #     rec.total_documents = len(docs_ids)

    @api.multi
    def action_view_invoice(self):
        return self.mapped('document_id').action_view_invoice()


class Service(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    state = fields.Selection([('draft', 'Draft'),
                              ('request', 'Request'),
                              ('done', 'Done'),
                              ('paid', 'Paid')],
                             string='State', default='draft')
    account_invoice_ids = fields.One2many('account.invoice', 'fleet_vehicle_log_services_ids', string='Invoices', copy=False)
    cost_subtype_in_branch = fields.Boolean(related='cost_subtype_id.in_branch')
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', 'fleet.vehicle.log.services')],
                                     string='Attachments')
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")

    @api.multi
    def submit(self):
        self.vehicle_id.state_id = self.env.ref('fleet_rental_document.vehicle_state_inshop')
        self.write({'state': 'request'})

    @api.multi
    def un_submit(self):
        self.vehicle_id.state_id = self.env.ref('fleet_rental_document.vehicle_state_active')
        self.write({'state': 'draft'})

    @api.multi
    def confirm(self):
        self.vehicle_id.state_id = self.env.ref('fleet_rental_document.vehicle_state_active')
        self.write({'state': 'done'})

    @api.multi
    def approve(self):
        self.write({'state': 'paid'})

    @api.multi
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['domain'] = ['&', ('res_model', '=', 'fleet.vehicle.log.services'), ('res_id', 'in', self.ids)]
        return action

    @api.multi
    def _get_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'fleet.vehicle.log.services'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)


class ServiceType(models.Model):
    _inherit = 'fleet.service.type'

    in_branch = fields.Boolean(default=False, readonly=True, invisible=True)


