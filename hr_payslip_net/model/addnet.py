# -*- coding: utf-8 -*-
from openerp import api, _
from tempfile import NamedTemporaryFile
import xlwt
from datetime import datetime
import os
import itertools
import logging
from functools import partial
from itertools import repeat
from lxml import etree
from lxml.builder import E
import openerp
from openerp import SUPERUSER_ID
from openerp import tools
import openerp.exceptions
from openerp import fields, models
from openerp.service.db import check_super
from openerp.tools.translate import _
from openerp.http import request
from openerp.exceptions import UserError
from openerp.osv import osv

class hr_payslip(models.Model):
    #_name = "hr.payslip.add.net"
    _inherit = 'hr.payslip'
    _description = "This model adds NET field to hr.payslip"
    net = fields.Float('Net amount', compute='_setNetValue', readonly=True, store=True)

    @api.depends('details_by_salary_rule_category.code')
    def _setNetValue(self):
        for rec in self:
            net_lines = [r for r in rec.details_by_salary_rule_category if r.code == 'NET']
            if net_lines.__len__() == 0:
                continue
            rec.net = float(net_lines[0].amount)