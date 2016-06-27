# -*- coding: utf-8 -*-

from openerp import api, fields, models


class VehicleTransfer(models.Model):
    _name = 'fleet_booking.transfer'

    state = fields.Selection([('draft', 'Draft'),
                              ('transfer', 'Transfer'),
                              ('done', 'Done')],
                             string='State', default='draft')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    old_branch = fields.Many2one('fleet_branch.branch')
    source_branch = fields.Many2one('fleet_branch.branch', string='From', required=True)
    dest_branch = fields.Many2one('fleet_branch.branch', string='To', required=True)
    current_odometer = fields.Float(related='vehicle_id.odometer', string='Current odometer')
    vehicle_state_id = fields.Many2one(related='vehicle_id.state_id', string='Vehicle state')
    delivery_state = fields.Selection([('not_delivered', 'Not delivered'), ('delivered', 'Delivered')], string='Delivery state', default='not_delivered', readonly=True)
    receiving_state = fields.Selection([('not_received', 'Not received'), ('received', 'Received')], string='Receiving state', default='not_received', readonly=True)
    can_change_delivery_state = fields.Boolean(compute='get_can_change_delivery_state', default=False)
    can_change_receiving_state = fields.Boolean(compute='get_can_change_receiving_state', default=False)

    @api.multi
    def submit(self):
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id.id)
        self.old_branch = vehicle.branch_id
        vehicle.branch_id = False
        self.write({'state': 'transfer'})

    @api.multi
    def un_submit(self):
        active_vehicle_state = self.env['fleet.vehicle.state'].browse(2)
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id.id)
        vehicle.state_id = active_vehicle_state
        vehicle.branch_id = self.old_branch
        self.write({'state': 'draft'})

    @api.multi
    def confirm_delivery(self):
        self.write({'delivery_state': 'delivered'})
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id.id)
        in_transfer_vehicle_state = self.env['fleet.vehicle.state'].browse(5)
        vehicle.state_id = in_transfer_vehicle_state
        if self.receiving_state == 'received':
            self.write({'state': 'done'})
            active_vehicle_state = self.env['fleet.vehicle.state'].browse(2)
            vehicle.state_id = active_vehicle_state
            vehicle.branch_id = self.dest_branch

    @api.multi
    def un_confirm_delivery(self):
        in_transfer_vehicle_state = self.env['fleet.vehicle.state'].browse(5)
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id.id)
        vehicle.state_id = in_transfer_vehicle_state
        vehicle.branch_id = False
        self.write({'state': 'transfer', 'delivery_state': 'not_delivered'})

    @api.multi
    def confirm_receiving(self):
        self.write({'receiving_state': 'received'})
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id.id)
        in_transfer_vehicle_state = self.env['fleet.vehicle.state'].browse(5)
        vehicle.state_id = in_transfer_vehicle_state
        if self.delivery_state == 'delivered':
            self.write({'state': 'done'})
            active_vehicle_state = self.env['fleet.vehicle.state'].browse(2)
            vehicle.state_id = active_vehicle_state
            vehicle.branch_id = self.dest_branch

    @api.multi
    def un_confirm_receiving(self):
        in_transfer_vehicle_state = self.env['fleet.vehicle.state'].browse(5)
        vehicle = self.env['fleet.vehicle'].browse(self.vehicle_id.id)
        vehicle.state_id = in_transfer_vehicle_state
        vehicle.branch_id = False
        self.write({'state': 'transfer', 'receiving_state': 'not_received'})

    @api.onchange('current_odometer')
    @api.multi
    def on_change_current_odometer(self):
        for rec in self:
            vehicle = self.env['fleet.vehicle'].browse(rec.vehicle_id.id)
            if vehicle.id:
                vehicle.odometer = rec.current_odometer

    @api.onchange('vehicle_id')
    @api.multi
    def on_change_vehicle_id(self):
        for rec in self:
            rec.source_branch = rec.vehicle_id.branch_id

    @api.multi
    def get_can_change_delivery_state(self):
        for record in self:
            if (self.env.user.branch_id.id == self.source_branch.id) and (self.env.ref('fleet_booking.group_branch_officer') in self.env.user.groups_id):
                record.can_change_delivery_state = True

    @api.multi
    def get_can_change_receiving_state(self):
        for record in self:
            if (self.env.user.branch_id.id == self.dest_branch.id) and (self.env.ref('fleet_booking.group_branch_officer') in self.env.user.groups_id):
                record.can_change_receiving_state = True

