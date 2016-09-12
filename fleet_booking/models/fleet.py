# -*- coding: utf-8 -*-
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class Vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    _inherits = {'fleet_rental.document': 'document_id'}
    document_id = fields.Many2one('fleet_rental.document',
                                  required=True, ondelete='restrict', auto_join=True)
    asset_id = fields.Many2one('account.asset.asset', ondelete='restrict', readonly=True, copy=False)
    product_id = fields.Many2one('product.product', 'Vehicle Product', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', copy=False)
    model_year = fields.Date('Model Year')
    paid = fields.Float(string='Paid amount', related="document_id.paid_amount", store=True, readonly=True)
    remain = fields.Float(string='Remaining amount', compute="_compute_remaining_amount",
                          store=True, readonly=True)
    reg_expiry = fields.Date('Registration expiry')
    ins_expiry = fields.Date('Insurance expiry')
    next_maintain = fields.Date('Next maintenance')
    payments_ids = fields.One2many('account.invoice', 'fleet_vehicle_id', string='Payments')
    depreciation_ids = fields.One2many(related='asset_id.depreciation_line_ids')
    state_id = fields.Many2one('fleet.vehicle.state', readonly=True, ondelete="restrict",
                               default=lambda self: self.env.ref('fleet_rental_document.vehicle_state_active').id,
                               copy=False)
    lease_installment_date_ids = fields.Many2many('fleet_booking.installment_date',
                                                  'fleet_booking_lease_dates_rel')
    insurance_installment_date_ids = fields.Many2many('fleet_booking.installment_date',
                                                      'fleet_booking_insurance_dates_rel')
    account_asset_id = fields.Many2one('account.account', string='Accumulated Depreciation Account',
                                       domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    account_depreciation_id = fields.Many2one('account.account', string='Depreciation Expense Account',
                                              domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    removal_reason = fields.Selection([('damage', 'Damage'),
                                       ('sold', 'Sold'),
                                       ('end-of-life', 'End-of-Life')],
                                      string='Removal reason', required=True)
    selling_price = fields.Float(string='Selling price')
    active = fields.Boolean(default=True)

    @api.depends('car_value', 'paid')
    def _compute_remaining_amount(self):
        for record in self:
            record.remain = record.car_value - record.paid

    @api.multi
    def action_view_invoice(self):
        return self.mapped('document_id').action_view_invoice()


class Service(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    state = fields.Selection([('draft', 'Draft'),
                              ('request', 'Request'),
                              ('done', 'Done'),
                              ('paid', 'Closed')],
                             string='State', default='draft')
    maintenance_type = fields.Selection([('accident', 'Accident'),
                                         ('emergency', 'Emergency'),
                                         ('periodic', 'Periodic'),
                                         ('in-branch', 'In-Branch')],
                                        string='Maintenance Type', default='in-branch', required=True)
    account_invoice_ids = fields.One2many('account.invoice', 'fleet_vehicle_log_services_ids',
                                          string='Invoices', copy=False)
    cost_subtype_in_branch = fields.Boolean(related='cost_subtype_id.in_branch')
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', 'fleet.vehicle.log.services')],
                                     string='Attachments')
    attachment_number = fields.Integer(compute='_get_attachment_number', string="Number of Attachments")
    service_line_ids = fields.One2many('fleet.vehicle.service.line', 'service_log_id')

    @api.multi
    def submit(self):
        if self.maintenance_type != 'in-branch':
            self.vehicle_id.sudo().state_id = self.env.ref('fleet_rental_document.vehicle_state_inactive')
            self.write({'state': 'request'})
        else:
            self.vehicle_id.sudo().state_id = self.env.ref('fleet_rental_document.vehicle_state_active')
            self.write({'state': 'done'})

    @api.multi
    def confirm(self):
        self.vehicle_id.state_id = self.env.ref('fleet_rental_document.vehicle_state_active')
        self.write({'state': 'done'})

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


class FleetVehicleServiceLine(models.Model):
    _name = 'fleet.vehicle.service.line'

    item = fields.Char(string='Item', required=True)
    cost = fields.Float(string='Cost', digits_compute=dp.get_precision('Product Price'))
    debit_account = fields.Many2one('account.account', string='Debit Account')
    credit_account = fields.Many2one('account.account', string='Credit Account')
    service_log_id = fields.Many2one('fleet.vehicle.log.services')
    move_id = fields.Many2one('account.move', string='Maintenance Entry')
    move_check = fields.Boolean(compute='_get_move_check', string='Posted', store=True)

    @api.one
    @api.depends('move_id')
    def _get_move_check(self):
        self.move_check = bool(self.move_id)

    @api.multi
    def create_move(self, journal_id, post_move=True):
        created_moves = self.env['account.move']
        for line in self:
            move_date = fields.Date.context_today(self)
            amount = line.cost
            journal_id = journal_id
            partner_id = line.service_log_id.sudo().vehicle_id.partner_id.id
            move_line_1 = {
                'name': line.item,
                'account_id': line.credit_account.id,
                'debit': 0.0,
                'credit': amount,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'date': move_date,
            }
            move_line_2 = {
                'name': line.item,
                'account_id': line.debit_account.id,
                'credit': 0.0,
                'debit': amount,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'date': move_date,
            }
            move_vals = {
                'date': move_date,
                'journal_id': journal_id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
                }
            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if post_move and created_moves:
            created_moves.post()
        return created_moves.ids
