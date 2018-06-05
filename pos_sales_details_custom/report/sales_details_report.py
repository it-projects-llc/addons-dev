# Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, api
from datetime import datetime
# import wdb


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, configs=False):
        result = super(ReportSaleDetails, self).get_sale_details(date_start, date_stop, configs)
        result['user_name'] = self.env['res.users'].browse(self.env.context['uid']).name
        pos_session_ids = self.env['pos.session'].search([('config_id', 'in', configs.ids)])
        pos_session_refs = [p_s.name for p_s in pos_session_ids]
        result['pos_names'] = ', '.join([pos.name for pos in configs])
        pos_orders = self.env['pos.order'].search([('session_id', 'in', pos_session_ids.ids)])
        # wdb.set_trace()
        result['order_num'] = len(pos_orders)
        for pay in result['payments']:
            pay['pay_num'] = len(self.env['account.bank.statement.line'].search([('journal_id.name', '=', 'Cash'),
                                                                                 ('ref', 'in', pos_session_refs)]))

        result['payments'] += [{
            'name': 'Total',
            'total': sum([p['total'] for p in result['payments']] + [0]),
            'pay_num': sum([p['pay_num'] for p in result['payments']] + [0]),
        }]

        result['cash_control'] = []
        for conf in configs:
            for session in conf.session_ids:
                lines_in = session.cash_register_id.cashbox_start_id.cashbox_lines_ids
                lines_out = session.cash_register_id.cashbox_end_id.cashbox_lines_ids
                lines_out_numbers = [l.number for l in lines_out]
                lines_out_used = []
                for line in lines_in:
                    if line.number in lines_out_numbers:
                        in_array = lines_out_numbers.index(line.number)
                        result['cash_control'] += [{
                            'number': line.number,
                            'coin_in': line.coin_value,
                            'subtotal_in': line.subtotal,
                            'coin_out': lines_out[in_array].coin_value,
                            'subtotal_out': lines_out[in_array].subtotal,
                        }]
                        lines_out_used += [lines_out[in_array]]
                    else:
                        result['cash_control'] += [{
                            'number': line.number,
                            'coin_in': line.coin_value,
                            'subtotal_in': line.subtotal,
                            'coin_out': 0,
                            'subtotal_out': 0,
                        }]
                for i in list(set(lines_out) - set(lines_out_used)):
                    result['cash_control'] += [{
                        'number': i.number,
                        'coin_in': 0,
                        'subtotal_in': 0,
                        'coin_out': i.coin_value,
                        'subtotal_out': i.subtotal,
                    }]

        result['put_in_out'] = []
        for ps in pos_session_ids:
            for rec in ps.pos_cash_box_ids:
                result['put_in_out'] += [{
                    'name': rec.name,
                    'amount': rec.put_type == 'in' and rec.amount or -rec.amount,
                    'datetime': rec.datetime
                }]

        # result['closing'] = []
        # for ps in pos_session_ids:
        #     put_inout = ps.pos_cash_box_ids and sum([(cb.put_type == 'in' and cb.amount or -cb.amount) for cb in ps.pos_cash_box_ids]) or 0
        #     theor_end = ps.cash_register_balance_start + ps.cash_register_total_entry_encoding + put_inout
        #     result['closing'] += [{
        #         'theoretical_closing_balance': theor_end,
        #         'closing_difference': ps.cash_register_difference,
        #         'real_closing_balance': ps.cash_register_difference + theor_end,
        #     }]

        result['closing'] = []
        for ps in pos_session_ids:
            put_inout = ps.pos_cash_box_ids and sum([(cb.put_type == 'in' and cb.amount or -cb.amount) for cb in ps.pos_cash_box_ids]) or 0
            theor_end = ps.cash_register_balance_start + ps.cash_register_total_entry_encoding + put_inout
            result['closing'] += [{
                'theoretical_closing_balance': theor_end,
                'closing_difference': ps.cash_register_difference,
                'real_closing_balance': ps.cash_register_difference + theor_end,
            }]

        put_inout = 0
        for ps in pos_session_ids:
            put_inout += ps.pos_cash_box_ids and sum(
                [(cb.put_type == 'in' and cb.amount or -cb.amount) for cb in ps.pos_cash_box_ids]) or 0
        result['theoretical_closing_balance'] = put_inout
        result['closing_difference'] = sum([ps.cash_register_difference for ps in pos_session_ids] + [0])
        result['real_closing_balance'] = result['closing_difference'] + result['theoretical_closing_balance'] - result['expenses_total']
        result['date'] = datetime.now().strftime('%y.%m.%d')

        result['cashiers'] = []
        result['returns'] = []
        print('===============================')
        print(result)
        print('===============================')
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
            prod['total'] = line.price_subtotal

        print('-------------------------------')
        print(result)
        print('-------------------------------')
        return result
