# -*- coding: utf-8 -*-

from openerp import api, fields, models


# INHERITED MODELS

class HrDepartment(models.Model):

    _name = "fleet_booking.branch"
    _inherit = 'hr.department'

    city = fields.Char(string='City')
    phone = fields.Char(string='Phone')
    branch_target = fields.Char(string='Branch Target')


class Person(models.Model):

    _inherit = 'res.partner'

    id_type = fields.Selection(
        [(u'National Id', u'National Id'), (u'Iqama', u'Iqama'),
         (u'Passport', u'Passport')],
        string='ID Type',
        )
    issuer = fields.Char(string='Issuer string')
    issuer_date = fields.Date(string='Date of Issue')
    license_type = fields.Selection([(u'Private', u'Private'),
                                     (u'General', u'General'),
                                     (u'International', u'International')],
                                    string='License Type')
    license_number = fields.Char(string='License Number')
    license_expiry_date = fields.Date(string='License Expiry Date')
    third_name = fields.Char(string='Third Name')
    family_name = fields.Char(string='Family Name')

    def check_age(self, cr, uid, ids, context=None, parent=None):
        for r in self.browse(cr, uid, ids, context=context):
            if r.customer and r.birthdate_date and r.age < 21:
                return False
        return True

    _constraints = [
        (check_age, 'Age restriction. Person must be elder than 20.', ['birthdate_date']),
    ]


class FleetBranch(models.Model):

    _inherit = 'fleet.vehicle'

    branch = fields.Many2one('fleet_booking.branch')


class Fleet(models.Model):

    _inherit = 'fleet.vehicle'

    colour = fields.Selection([('black', 'Black'),
                              ('blue', 'Blue'),
                              ('red', 'Red'),
                              ('white', 'White'),
                              ('sliver', 'Sliver'),
                              ('yellow', 'Yellow'),
                              ('green', 'Green'),
                              ('gold', 'Gold'),
                              ('orange', 'Orange'),
                              ('brown', 'Brown'),
                              ], string='Color', default='black')
    model_year = fields.Integer('Model Year')
    daily_rate = fields.Float('Daily Rate')
    extra_rate = fields.Float('Rate per extra km')
    allowed_per_day = fields.Float('Allowed km per day')
    paid = fields.Float('Paid amount')
    remain = fields.Float('Remaining amount')
    reg_expiry = fields.Date('Registration expiry')
    ins_expiry = fields.Date('Insurance expiry')
    next_maintain = fields.Date('Next maintenance')
    payments_ids = fields.One2many('account.invoice', 'fleet_vehicle_id', string='Payments')
    total_invoiced = fields.Float(default=0)
    insurance_ids = fields.One2many('fleet_booking.insurances', 'fleet_vehicle_id', string='Insurance Installments')
    deprecation_ids = fields.One2many(related='asset_id.depreciation_line_ids')
    asset_id = fields.Many2one('account.asset.asset', compute='compute_asset', inverse='asset_inverse')
    asset_ids = fields.One2many('account.asset.asset', 'vehicle_id')
    # TODO Rename deprecation to depreciation

    @api.one
    @api.depends('asset_ids')
    def compute_asset(self):
        if len(self.asset_ids) > 0:
            self.asset_id = self.asset_ids[0]

    @api.one
    def asset_inverse(self):
        new_asset = self.env['account.asset.asset'].browse(self.asset_id.id)
        if len(self.asset_ids) > 0:
            asset = self.env['account.asset.asset'].browse(self.asset_ids[0].id)
            asset.vehicle_id = False
        new_asset.vehicle_id = self

    # def act_show_invoices(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = {}
    #     res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'account', 'action_invoice_refund_out_tree_form',
    #                                                             context=context)
    #     res['context'] = context
    #     # res['context'].update({
    #     #     'default_vehicle_id': ids[0],
    #     #     'search_default_parent_false': True
    #     # })
    #     # res['domain'] = [('vehicle_id', '=', ids[0])]
    #     return res


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

    @api.multi
    def submit(self):
        in_shop_vehicle_state = self.env['fleet.vehicle.state'].browse(1)
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id.id)
        vehicle.state_id = in_shop_vehicle_state
        self.write({'state': 'request'})

    @api.multi
    def confirm(self):
        active_vehicle_state = self.env['fleet.vehicle.state'].browse(2)
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id.id)
        vehicle.state_id = active_vehicle_state
        self.write({'state': 'done'})

    @api.multi
    def approve(self):
        self.write({'state': 'paid'})


class ServiceType(models.Model):
    _inherit = 'fleet.service.type'

    in_branch = fields.Boolean(default=False, readonly=True, invisible=True)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fleet_vehicle_log_services_ids = fields.Many2one('fleet.vehicle.log.services')
    fleet_vehicle_id = fields.Many2one('fleet.vehicle')


class Asset(models.Model):
    _inherit = 'account.asset.asset'

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')


# OWN MODELS


class InsuranceInstallments(models.Model):
    _name = 'fleet_booking.insurances'
    _order = 'fleet_vehicle_id, sequence, id'

    fleet_vehicle_id = fields.Many2one('fleet.vehicle')
    sequence = fields.Integer(default=1,
                              help="Gives the sequence of this line when displaying the vehicle.")
    insurance_date = fields.Datetime(string='Date', default=fields.Datetime.now())
    amount = fields.Float(string='Amount')
