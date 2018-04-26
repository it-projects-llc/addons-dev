# -*- coding: utf-8 -*-
# Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError


class ReportProductLabel(models.AbstractModel):
    _name = 'report.product_label_custom.report_product_label'
    
    @api.model
    def render_html(self, docids, data=None):
        wizard = self.env['product.label.wizard'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': 'product.label.report.settings',
            'data': data,
            'docs': wizard.settings_ids,
        }
        return self.env['report'].render('product_label_custom.report_product_label', docargs)
