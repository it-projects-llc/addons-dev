# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Company(models.Model):
    _inherit = "res.company"

    inn = fields.Char(related='partner_id.inn', string='INN', size=12)
    kpp = fields.Char(related='partner_id.kpp', string='KPP', size=9)
    okpo = fields.Char(related='partner_id.okpo', string='OKPO', size=14)
