# -*- coding: utf-8 -*-
# Copyright 2018 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


import base64
from mako.template import Template
import os

from odoo import models, api, fields


def get_template_path(template_name):
    current_file_path = os.path.dirname(os.path.realpath(__file__))
    # We put templates to the static/lib so CI checks is ignored
    return os.path.join(os.path.split(current_file_path)[0], 'static', 'lib', 'templates', template_name)


class CiJsTour(models.Model):
    _name = "ci_js.tour"
    _description = "Model of tour"
    name = fields.Char(help="Tour name which used as argument in tour.register", required=True, string="Tour")
    start_url = fields.Char(help="Open link before running the tour", required=True)
    skip_enabled = fields.Boolean("Skip enabled", default=False)
    assets = fields.Selection([
        ('assets_backend', 'Backend'),
        ('assets_frontend', 'Front-end'),
        ('pos_assets', 'Pos')
    ], help="Choose assets which tour needs")
    wait_for = fields.Char(help="Wait for deffered object before running the script")
    set_ids = fields.One2many("ci_js.tour.set", "tour_id", string="Sets")
    tour_content = fields.Char(compute="_compute_tour_text")
    file = fields.Binary(readonly=True, compute="_compute_tour_js", )
    file_name = fields.Char()

    @api.depends('name', 'start_url', 'skip_enabled', 'wait_for', 'set_ids')
    def _compute_tour_text(self):
        path_to_template = get_template_path('tour_template.js')
        js_template = Template(
            filename=path_to_template,
            input_encoding='utf-8',
            output_encoding='utf-8',
        )
        for rec in self:
            rec.tour_content = js_template.render(
                tour_name=rec.name,
                start_url=rec.start_url,
                wait_for=rec.wait_for,
                skip_enabled=rec.skip_enabled,
                set_ids=rec.set_ids,
            )

    @api.depends('tour_content')
    def _compute_tour_js(self):
        for rec in self:
            rec.file = base64.b64encode(rec.tour_content)
            rec.file_name = 'tour.js'

    # Заготовка метода для подключения тура в ассетсы
    # TODO закончить проверку работоспособности способа подключения тура на основе примера из модуля theme_kit
    # @api.multi
    # def set_tour(self):
    #     custom_js_arch = '''<?xml version="1.0"?>
    #     <t t-name="ci_js.tour_script">
    #     %s
    #     </t>
    #     '''
    #     tour = self.env.ref('ci_js.tour_script')
    #     code = ''
    #     if self.tour_content:
    #         code = self.tour_content
    #     arch = custom_js_arch % code
    #     tour.write({'arch': arch})


class CiJsTourSet(models.Model):
    _name = "ci_js.tour.set"
    _description = "Set of steps"
    _order = "sequence"
    name = fields.Char(required=True, string="Set")
    sequence = fields.Integer(help="Sequence number of the set in the sets list", default=10)
    args = fields.Text(help="List of value")
    # kwargs = fields.Char(help="Dictionary of value")
    template_id = fields.Many2one("ci_js.template", string="Template")
    tour_id = fields.Many2one('ci_js.tour')
    # step_id = fields.Many2one(help='Use either Template+args,kwargs OR Single Step')
    # set_content_without_args = fields.Char(compute="_compute_set_without_args", store=True)
    content_with_args = fields.Char(compute="_compute_set_with_args")

    @api.depends('template_id')
    def _compute_set_with_args(self):
        for rec in self:
            if rec.template_id.template:
                js_template = Template(rec.template_id.template)
                rec.content_with_args = js_template.render(args=rec.args or [], name=rec.name)


class CiJsTemplate(models.Model):
    _name = "ci_js.template"
    _description = "Step set template"
    name = fields.Char(string="Template name")
    step_ids = fields.One2many("ci_js.tour.set.step", "template_id", string="Steps")
    template = fields.Char(compute="_compute_template")

    @api.depends('step_ids')
    def _compute_template(self):
        path_to_template = get_template_path('set_template.js')
        js_template = Template(
            filename=path_to_template,
            input_encoding='utf-8',
            output_encoding='utf-8',
        )
        for rec in self:
            rec.template = js_template.render(step_ids=rec.step_ids, name="${name}",)


class CiJsTourSetStep(models.Model):
    _name = "ci_js.tour.set.step"
    _description = "Step"
    content = fields.Char(help="Name or title of the step", default="click on add to cart")
    trigger = fields.Char(help="Where to place tip. In js tests: where to click", required=True,
                          default='#product_detail form[action^="/shop/cart/update"] .btn')
    extra_trigger = fields.Char(help="When this becomes visible, the tip is appeared. In js tests: when to click")
    timeout = fields.Integer(help="Max time to wait for conditions")
    position = fields.Selection([
        ("left", "Left"),
        ("right", "Right"),
        ("top", "Top"),
        ("bottom", "Bottom"),
    ], help="How to show tip")
    width = fields.Integer(help="Width in px of the tip when opened", default=270)
    edition = fields.Selection([
        ("community", "Community"),
        ("enterprise", "Enterprise"),
        ("both", "Both"),
    ], help="", default="both")
    run = fields.Char(help="What to do when tour runs automatically")
    auto = fields.Boolean(help="Step will be skipped")
    # TODO: скрыть это поле в виде, так как оно техническое(можно почитать в доках о полях One2many)
    template_id = fields.Many2one('ci_js.template')
    # TODO: изучить механизм генерации порядкового поля и изменения порядка в отображении.
    sequence = fields.Integer('Sequence')
