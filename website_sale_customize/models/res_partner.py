# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_delivery = fields.Boolean('Это доставщик')
    fleet_id = fields.Many2one("fleet.vehicle", string="Автомобиль")
