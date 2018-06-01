from odoo import models, fields, api
import wdb


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
        result['order_num'] = len(pos_orders)
        for pay in result['payments']:
            pay['pay_num'] = len(self.env['account.bank.statement.line'].search([('journal_id.name', '=', 'Cash'),
                                                                                 ('ref', 'in', pos_session_refs)]))
        payment_total = {
            'name': 'Total',
            'total': sum([p['total'] for p in result['payments']] + [0]),
            'pay_num': sum([p['pay_num'] for p in result['payments']] + [0]),
        }
        result['payments'] += [payment_total]
        result['cashiers'] = []

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

        wdb.set_trace()
        cash_res = []
        for conf in configs:
            for session in conf.session_ids:
                line_in = session.cash_register_id.cashbox_start_id.cashbox_lines_ids
                line_out = session.cash_register_id.cashbox_end_id.cashbox_lines_ids
                cash_res += [{
                    'number': line_out.number,
                    'coin_in': line_in.coin_value,
                    'subtotal_in': line_in.subtotal,
                    'coin_out': line_out.coin_value,
                    'subtotal_out': line_out.subtotal,
                }]

        result['put_in_out'] = cash_res

        print('--------------------5')
        print(result)
        print('--------------------5')

        return result
