# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api
from datetime import datetime
from odoo.addons.point_of_sale.wizard.pos_box import PosBox


class PosSession(models.Model):
    _inherit = 'pos.session'

    pos_cash_box_ids = fields.One2many('pos.cash.box', 'session_id')
    opened_by = fields.Many2one('res.users', string='User opened the session')
    closed_by = fields.Many2one('res.users', string='User closed the session')

    @api.multi
    def action_pos_session_open(self):
        res = super(PosSession, self).action_pos_session_open()
        self.write({
            'opened_by': self.env.context.get('uid')
        })
        return res

    @api.multi
    def action_pos_session_close(self):
        res = super(PosSession, self).action_pos_session_close()
        self.write({
            'closed_by': self.env.context.get('uid')
        })
        return res


class CashBoxOut(models.Model):
    _name = 'pos.cash.box'

    name = fields.Char(string='Reason', required=True)
    amount = fields.Float(string='Amount', digits=0, required=True)
    datetime = fields.Datetime(string='Date', required=True)
    session_id = fields.Many2one('pos.session', string='POS Session')
    put_type = fields.Selection([
        ('in', 'Put in'),
        ('out', 'Put out')
        ], string='Type')


class PosBoxIn(PosBox):
    _inherit = 'cash.box.in'

    @api.multi
    def _run(self, records):
        res = super(PosBoxIn, self)._run(records)
        active_model = self.env.context.get('active_model', False)
        active_ids = self.env.context.get('active_ids', [])
        if active_model == 'pos.session' and active_ids:
            for rec in self:
                self.env['pos.cash.box'].create({
                    'name': rec.name,
                    'amount': rec.amount,
                    'session_id': active_ids[0],
                    'put_type': 'in',
                    'datetime': datetime.now(),
                })
        return res


class PosBoxOut(PosBox):
    _inherit = 'cash.box.out'

    @api.multi
    def _run(self, records):
        res = super(PosBoxOut, self)._run(records)
        active_model = self.env.context.get('active_model', False)
        active_ids = self.env.context.get('active_ids', [])
        if active_model == 'pos.session' and active_ids:
            for rec in self:
                self.env['pos.cash.box'].create({
                    'name': rec.name,
                    'amount': rec.amount,
                    'session_id': active_ids[0],
                    'put_type': 'out',
                    'datetime': datetime.now(),
                })
        return res


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    datetime = fields.Datetime(required=True, string="Start date", default=fields.Datetime.now)
