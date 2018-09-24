# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, api
from datetime import datetime


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, configs=False):
        result = super(ReportSaleDetails, self).get_sale_details(date_start, date_stop, configs)
        active_user = self.env['res.users'].browse(self.env.context['uid'])
        pos_session_ids = self.env['pos.session'].search([('config_id', 'in', configs.ids),
                                                          ('start_at', '<', date_stop),
                                                          ('stop_at', '>', date_start)])
        pos_session_refs = [p_s.name for p_s in pos_session_ids]
        pos_orders = self.env['pos.order'].search([('session_id', 'in', pos_session_ids.ids),
                                                   ('date_order', '<', date_stop),
                                                   ('date_order', '>', date_start)])
        result['user_name'] = active_user.name
        result['pos_names'] = ', '.join([pos.name for pos in configs])
        result['order_num'] = len(pos_orders)

        all_payments = self.env['account.bank.statement.line'].search([('ref', 'in', pos_session_refs),
                                                                       ('datetime', '>=', date_start),
                                                                       ('datetime', '<=', date_stop)])

        for pay in all_payments.filtered(lambda p: p.amount > 0):
            journal = self.env['account.journal'].search([('name', '=', pay.journal_id.name)], limit=1)
            for i in result['payments']:
                if i['name'] == journal.name:
                    i['pay_num'] = 'pay_num' in i and i['pay_num'] + 1 or 1
                    i['type'] = journal.type

        result['payments_total'] = {
            'name': 'Total',
            'total': sum([p['total'] for p in result['payments']] + [0]),
            'pay_num': sum([('pay_num' in p and p['pay_num'] or 0) for p in result['payments']] + [0]),
            'cash': sum([p['total'] for p in result['payments'] if p['type'] == 'cash'] + [0]),
        }

        result['card_payments'] = []
        for p in all_payments.filtered(lambda r: r.journal_id.type != 'cash'):
            result['card_payments'] += [{
                'ref': p.ref,
                'datetime': p.statement_id.date_done,
                'journal': p.journal_id.name,
                'cashier': p.pos_statement_id.user_id.name,
                'amount': p.amount,
            }]
        result['card_payments_total'] = sum([p['amount'] for p in result['card_payments']] + [0])

        result['cash_control'] = []
        lines_in = []
        lines_out = []
        result['sessions'] = []
        for session in pos_session_ids:
            result['sessions'].append({
                'name': session.name,
                'opened_by': session.opened_by.name,
                'closed_by': session.closed_by.name
            })
            lines_in += session.cash_register_id.cashbox_start_id.cashbox_lines_ids
            lines_out += session.cash_register_id.cashbox_end_id.cashbox_lines_ids
        for i in lines_out:
            in_report = False
            for j in result['cash_control']:
                if i.coin_value == j['coin_value']:
                    j['coin_out'] += i.number
                    j['subtotal_out'] += i.subtotal
                    in_report = True
            if not in_report:
                result['cash_control'] += [{
                    'coin_value': i.coin_value,
                    'coin_in': 0,
                    'subtotal_in': 0,
                    'coin_out': i.number,
                    'subtotal_out': i.subtotal,
                }]
        for i in lines_in:
            in_report = False
            for j in result['cash_control']:
                if i.coin_value == j['coin_value']:
                    j['coin_in'] += i.number
                    j['subtotal_in'] += i.subtotal
                    in_report = True
            if not in_report:
                result['cash_control'] += [{
                    'coin_value': i.coin_value,
                    'coin_in': i.number,
                    'subtotal_in': i.subtotal,
                    'coin_out': 0,
                    'subtotal_out': 0,
                }]

        result['put_in_out'] = []
        for ps in pos_session_ids:
            for rec in ps.pos_cash_box_ids:
                if rec.datetime <= date_stop and rec.datetime >= date_start:
                    result['put_in_out'] += [{
                        'name': rec.name,
                        'amount': rec.put_type == 'in' and rec.amount or -rec.amount,
                        'datetime': rec.datetime
                    }]
        result['put_in_out_total'] = sum([l['amount'] for l in result['put_in_out']] + [0])

        result['closing_difference'] = result['real_closing_balance'] = result['cash_register_balance_end'] = result['opening_balance'] = 0
        put_inout = 0
        for ps in pos_session_ids:
            put_inout += ps.pos_cash_box_ids and sum(
                [(cb.put_type == 'in' and cb.amount or -cb.amount) for cb in ps.pos_cash_box_ids]) or 0
            result['real_closing_balance'] += ps.cash_register_balance_end_real
            result['opening_balance'] += ps.cash_register_balance_start

        result['theoretical_closing_balance'] = (result['opening_balance'] + put_inout +
                                                 result['payments_total']['total'] +
                                                 result['expenses_total'] + result['total_invoices'])
        result['cash_register_balance_end'] = (result['opening_balance'] + put_inout +
                                               result['payments_total']['cash'] +
                                               result['expenses_total'] + result['total_invoices_cash'])
        result['closing_difference'] = result['cash_register_balance_end'] - result['real_closing_balance']
        result['date'] = datetime.now().strftime('%y/%m/%d')

        result['returns_total'] = 0
        result['cashiers'] = result['returns'] = []
        if not pos_orders.ids:
            return result

        self.env.cr.execute("""
            SELECT DISTINCT po.user_id
            FROM pos_order AS po
            WHERE po.id IN %s
            GROUP BY po.user_id
            """, (tuple(pos_orders.ids),))
        cashiers = [c['user_id'] for c in self.env.cr.dictfetchall()]
        for c in cashiers:
            user = self.env['res.users'].browse(c)
            orders = pos_orders.filtered(lambda po: po.user_id == user)
            result['cashiers'] += [{
                'name': user.name,
                'sale_num': len(orders),
                'total': sum([o.amount_total for o in orders])
            }]

        self.env.cr.execute("""
            SELECT po.name as po_name,
                pol.id as line_id,
                pol.product_id as product_id, 
                pt.name as product_name, 
                po.user_id as user_id, 
                pol.qty as qty,
                rp.name as cashier
            FROM pos_order_line AS pol,
                 pos_order AS po,
                 product_product as pp,
                 product_template as pt,
                 res_partner AS rp,
                 res_users AS ru
            WHERE pol.order_id = po.id
                AND po.id IN %s
                AND pol.product_id = pp.id
                AND pp.product_tmpl_id = pt.id
                AND ru.partner_id = rp.id
                AND po.user_id = ru.id
                AND pol.qty < 0
            """, (tuple(pos_orders.ids),))
        result['returns'] = self.env.cr.dictfetchall()

        for prod in result['returns']:
            line = self.env['pos.order.line'].browse(prod['line_id'])
            prod['customer'] = line.order_id.partner_id.name or ''
            prod['total'] = line.price_subtotal_incl

        result['returns_total'] = sum([l['total'] for l in result['returns']] + [0])

        return result
