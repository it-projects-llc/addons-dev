# -*- coding: utf-8 -*-
# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields, api
from odoo.addons.base.ir.ir_qweb.qweb import QWeb
from lxml import etree


class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_label_id = fields.Many2one('product.label', 'Default Label', help="Select label for the current product")

    @api.model
    def get_render_qweb(self, label_id):
        if not label_id:
            template = self.default_label_id.qweb_template
        else:
            template = self.env['product.label'].browse(label_id).qweb_template
        dom = etree.fromstring(template)
        html = QWeb().render(dom, {'product': self})
        return html


class ProductLabel(models.Model):
    _name = "product.label"

    name = fields.Char('Name', required=True)
    paper_format_id = fields.Many2one('report.paperformat', 'Paper format', required=True)
    qweb_template = fields.Text('Qweb', required=True)
