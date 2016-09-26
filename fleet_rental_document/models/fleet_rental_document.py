# -*- coding: utf-8 -*-
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class FleetRentalDocument(models.Model):
    _name = 'fleet_rental.document'

    invoice_line_ids = fields.One2many('account.invoice.line', 'fleet_rental_document_id',
                                       string='Invoice Lines', copy=False)
    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string='analytic account for document', readonly=True, copy=False)
    invoice_ids = fields.Many2many("account.invoice", string='Invoices',
                                   compute="_get_invoiced", readonly=True, copy=False)
    invoice_count = fields.Integer(string='# of Invoices', compute='_get_invoiced', readonly=True)

    paid_amount = fields.Float(string='Paid Amount', compute="_compute_paid_amount", store=True,
                               digits_compute=dp.get_precision('Product Price'), readonly=True)
    type = fields.Selection([
        ('rent', 'Rent'),
        ('extend', 'Extend'),
        ('return', 'Return'),
        ('vehicle', 'Vehicle'),
    ], readonly=True, index=True, change_default=True)

    @api.multi
    def action_view_invoice(self):
        invoice_ids = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree')
        if self._context.get('view_type', False) == 'supplier':
            list_view_id = self.env.ref('account.invoice_supplier_tree').id
            form_view_id = self.env.ref('account.invoice_supplier_form').id
        else:
            list_view_id = self.env.ref('account.invoice_tree').id
            form_view_id = self.env.ref('account.invoice_form').id

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form'],
                      [False, 'graph'], [False, 'kanban'], [False, 'calendar'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        if len(invoice_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % invoice_ids.ids
        elif len(invoice_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = invoice_ids.ids[0]
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.depends('invoice_line_ids')
    def _get_invoiced(self):

        for document in self:
            invoice_ids = document.invoice_line_ids.mapped('invoice_id')
            # Search for refunds as well
            refund_ids = self.env['account.invoice'].browse()
            if invoice_ids:
                refund_ids = refund_ids.search([('type', '=', 'out_refund'),
                                                ('origin', 'in', invoice_ids.mapped('number')),
                                                ('origin', '!=', False)])

            document.update({
                'invoice_count': len(set(invoice_ids.ids + refund_ids.ids)),
                'invoice_ids': invoice_ids.ids + refund_ids.ids,
            })

    @api.multi
    @api.depends('analytic_account_id.line_ids.move_id.balance_cash_basis')
    def _compute_paid_amount(self):
        for record in self:
            for line in record.analytic_account_id.line_ids:
                if line.amount > 0:
                    record.paid_amount += abs(line.move_id.balance_cash_basis)
                else:
                    record.paid_amount -= line.move_id.balance_cash_basis

    @api.multi
    def action_create_refund(self):
        pass
