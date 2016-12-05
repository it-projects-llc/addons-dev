# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Import(models.TransientModel):
    _inherit = "base_import.import"

    settings_id = fields.Many2one("base_import_map.map", string="Settings")

    def parse_preview(self, options, count=10):
        res = super(Import, self).parse_preview(options, count=10)
        if options.get('settings'):
            settings = self.env["base_import_map.map"].search([("id", "=", options.get('settings'))]).line_ids
            res['matches'] = {r.column_number: [str(r.field_name)] for r in settings}
        return res

    @api.multi
    def do(self, fields, options, dryrun=False):
        res = super(Import, self).do(fields, options, dryrun=False)
        if options['save_settings']:
            model_id = self.env["ir.model"].search([("model", "=", str(self.res_model))]).id
            new_settings = self.env["base_import_map.map"].create({
                "name": str(options['save_settings']),
                "model_id": model_id,
            })
            settings_line = self.env["base_import_map.line"]
            k = 0
            for field in fields:
                if field:
                    settings_line.create({
                        "setting_id": new_settings.id,
                        "field_name": field,
                        "column_number": k

                    })
                k += 1
        return res

class SettingImport(models.Model):
    _name = "base_import_map.map"

    name = fields.Char(string="Setting Name")
    external_id_generator = fields.Integer(string="External id")
    model_id = fields.Many2one("ir.model", string="Models")
    model = fields.Char(related="model_id.model")
    line_ids = fields.One2many("base_import_map.line", "setting_id", string="Settings line")


class SettingLineImport(models.Model):
    _name = "base_import_map.line"

    setting_id = fields.Many2one("base_import_map.map", string="Settings")
    field_name = fields.Char(string="Name")
    column_number = fields.Integer(string="Column number")
