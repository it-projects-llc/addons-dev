# Copyright 2018 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# -*- coding: utf-8 -*-
from odoo import api, models, fields


class CiJsTour(models.Model):
    # _inherit = ""
    _name = "ci_js.tour"
    tour_name = fields.Char()
    start_url = fields.Char()
    skip_enabled = fields.Boolean("Skip enabled")
    assets = fields.Selection([
        ('assets_backend', 'Backend'),
        ('assets_frontend', 'Front-end'),
        ('pos_assets', 'Pos')
    ])
    wait_for = fields.Char()  # Надо подумать про тип поля. Возможно нужен Selection
    set_ids = fields.One2many("ci_js.tour.set")


class CiJsTourSet(models.Model):
    # _inherit = ""
    _name = "ci_js.tour.set"
    set_name = fields.Char()
    sequence = fields.Integer()
    template_id = fields.Many2one("ci_js.template")
    args = fields.Char()  # "List of value"
    kwargs = fields.Char()  # "Dictionary of value"
    # step_id = fields.Many2one(help='Use either Template+args,kwargs OR Single Step')


class CiJsTemplate(models.Model):
    # _inherit = ""
    _name = "ci_js.template"
    template_name = fields.Char()
    step_ids = fields.One2many("ci_js.tour.set.step")


class CiJsTourSetStep(models.Model):
    # _inherit = ""
    _name = "ci_js.tour.set.step"
    content = fields.Char()
    trigger = fields.Char()
    extra_trigger = fields.Char()
    timeout = fields.Integer()
    position = fields.Selection([
        ("left", "left"),
        ("right", "right"),
        ("top", "top"),
        ("bottom", "bottom"),
    ])
    width = fields.Char()
    edition = fields.Selection([
        ("community", "Community"),
        ("enterprise", "Enterprise"),
        ("both", "Both"),
    ])
    run = fields.Char()
    auto = fields.Boolean()
