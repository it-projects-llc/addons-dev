# -*- coding: utf-8 -*-
# Copyright 2018 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, fields
# Не установлено:
from mako.template import Template


class CiJsTour(models.Model):
    _name = "ci_js.tour"
    tour_name = fields.Char(help="Tour name which used as argument in tour.register", required=True, default="tour_name_for_testing")
    start_url = fields.Char(help="Open link before running the tour", required=True)
    skip_enabled = fields.Boolean("Skip enabled", default=False)
    # Не нравится такой механизм работы с assets'ами. По логике может быть такой вариант, что тестировать нужно
    # в нескольких
    # assets = fields.Selection([
    #     ('assets_backend', 'Backend'),
    #     ('assets_frontend', 'Front-end'),
    #     ('pos_assets', 'Pos')
    # ], help="Choose assets which tour needs")
    wait_for = fields.Char(help="Wait for deffered object before running the script", default="base.ready()")
    set_ids = fields.One2many("ci_js.tour.set", "tour_id", string="Sets")

    # Пока не уверен насчет правильности использования декоратора
    def get_js_code(self):
        # Где должен находиться файл шаблона - отдельный вопрос, скорее всего не здесь
        js_template = Template(filename='../src/tour_template.js')

        return js_template.render(
            tour_name=self.tour_name,
            start_url=self.start_url,
            wait_for=self.wait_for,
            skip_enabled=self.skip_enabled,
            set_ids=self.set_ids,
        )


class CiJsTourSet(models.Model):
    _name = "ci_js.tour.set"
    set_name = fields.Char(help="Name that will be displayed in the sets list", required=True, default="test_set_name")
    # поле sequence, вероятно, не нужно отображать в интерфейсе, а вычислять автоматически(например при создании сетов они по умолчанию будут идти за друг другом, но можно перетащить один из сетов, тем самым помеять порядок)
    sequence = fields.Integer(help="Sequence number of the set in the sets list")
    # Пока не знаю как лучше принимать args и kwargs
    # args = fields.Char(help="List of value")
    # kwargs = fields.Char(help="Dictionary of value")
    template_id = fields.Many2one("ci_js.template")
    # Тест. Правильно ли я задаю здесь это поле, сделал так потому что в ci_js.tour ругается на set_ids, что поле
    # One2many должно иметь обязательный аргумент inverse_name.
    # Теперь интересно как с ним работать, вероятно, его надо автоматически задавать и не отображать в интерфейсе
    tour_id = fields.Many2one('ci_js.tour')
    # step_id = fields.Many2one(help='Use either Template+args,kwargs OR Single Step')

    def get_js_function(self):
        js_template = Template(filename='../src/set_template.js')
        return js_template.render(
            set_name=self.set_name,
            args=self.args,
            kwargs=self.kwargs,
            template_id=self.template_id,
        )


class CiJsTemplate(models.Model):
    _name = "ci_js.template"
    template_name = fields.Char(help="Name for easy template searching", default="test_template_name")
    step_ids = fields.One2many("ci_js.tour.set.step", "template_id")


class CiJsTourSetStep(models.Model):
    _name = "ci_js.tour.set.step"
    content = fields.Char(help="Name or title of the step", default="click on add to cart")
    trigger = fields.Char(help="Where to place tip. In js tests: where to click", required=True, default='#product_detail form[action^="/shop/cart/update"] .btn')
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
    # Тест. Я думаю что здесь не должно быть так, так как шаги скорее всего будут переиспользоваться, а не принадлежать
    # к одному шаблону
    template_id = fields.Many2one('ci_js.template')
