# -*- encoding: utf-8 -*-
from openerp import fields
from openerp import models


class Company(models.Model):
    _name = 'res.company'
    _inherit = ['res.company', 'base_details']

    def _model_selection(self):
        selection = super(Company, self)._model_selection()
        selection.append(('queue.management.branch', 'Queue Management Branch'))
        return selection
