# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Import(models.TransientModel):
    _inherit = "base_import.import"

    settings_id = fields.Many2one("base_import_map.map", string="Settings")

class SettingImport(models.Model):
    _name = "base_import_map.map"

    name = fields.Char(string="Setting Name")
    external_id_generator = fields.Char()
    model_id = fields.Many2one()
    line_ids = fields.One2many("base_import_map.line", "setting_id", string="Settings line")


class SettingLineImport(models.Model):
    _name = "base_import_map.line"

    setting_id = fields.Many2one("base_import_map.map", string="Settings")
    field_name = fields.Char()
    column_number = fields.Integer()
