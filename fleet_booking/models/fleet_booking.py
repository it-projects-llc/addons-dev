# -*- coding: utf-8 -*-

from openerp import api, fields, models


# INHERITED MODELS


class Person(models.Model):

    _inherit = 'res.partner'

    _sql_constraints = [('passport', 'unique(passport)', 'ID Number restriction. Person with same id number already exists.')]

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


class Vehicle(models.Model):

    _inherit = 'fleet.vehicle'

    model_year = fields.Integer('Model Year')
    paid = fields.Float('Paid amount')
    remain = fields.Float('Remaining amount')
    reg_expiry = fields.Date('Registration expiry')
    ins_expiry = fields.Date('Insurance expiry')
    next_maintain = fields.Date('Next maintenance')
    payments_ids = fields.One2many('account.invoice', 'fleet_vehicle_id', string='Payments')
    total_documents = fields.Integer(compute='_count_total_documents', string="Total documents", default=0)
    deprecation_ids = fields.One2many(related='asset_id.depreciation_line_ids')
    asset_id = fields.Many2one('account.asset.asset', compute='compute_asset', inverse='asset_inverse', string='Asset')
    asset_ids = fields.One2many('account.asset.asset', 'vehicle_id')
    # TODO Rename deprecation to depreciation

    @api.one
    @api.depends('asset_ids')
    def compute_asset(self):
        if len(self.asset_ids) > 0:
            self.asset_id = self.asset_ids[0]

    @api.one
    def asset_inverse(self):
        if not self.asset_id.id:
            return
        new_asset = self.env['account.asset.asset'].browse(self.asset_id.id)
        if len(self.asset_ids) > 0:
            asset = self.env['account.asset.asset'].browse(self.asset_ids[0].id)
            asset.vehicle_id = False
        new_asset.vehicle_id = self

    @api.multi
    def _count_total_documents(self):
        for rec in self:
            docs_ids = self.env['fleet_rental.document'].search([('vehicle_id.id', '=', rec.id)])
            rec.total_documents = len(docs_ids)


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
        self.vehicle_id.state_id = self.env.ref('fleet.vehicle_state_inshop')
        self.write({'state': 'request'})

    @api.multi
    def un_submit(self):
        self.vehicle_id.state_id = self.env.ref('fleet.vehicle_state_active')
        self.write({'state': 'draft'})

    @api.multi
    def confirm(self):
        self.vehicle_id.state_id = self.env.ref('fleet.vehicle_state_active')
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


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fleet_vehicle_log_services_ids = fields.Many2one('fleet.vehicle.log.services')
    fleet_vehicle_id = fields.Many2one('fleet.vehicle')


class Asset(models.Model):
    _inherit = 'account.asset.asset'

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')

# OWN MODELS
