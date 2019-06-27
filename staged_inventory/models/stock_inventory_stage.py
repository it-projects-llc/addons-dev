# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class StockInventoryStage(models.Model):
    _name = "stock.inventory.stage"
    _order = 'create_date desc'

    name = fields.Char('Name')
    barcode = fields.Char('Barcode')
    inventory_id = fields.Many2one(
        comodel_name='stock.inventory',
        string='Inventory',
    )
    state = fields.Selection(
        selection=[('open', 'Open'), ('done', 'Done')],
        string='Status',
        default='open',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
    )
    line_ids = fields.One2many(
        comodel_name='stock.inventory.stage.line',
        inverse_name='stage_id',
        string='Stage Lines',
    )
    note = fields.Char(
        string='Comment',
    )

    @api.onchange('barcode')
    def _onchange_barcode(self):
        self.ensure_one()
        if not self.inventory_id or self.inventory_id.state not in ['draft', 'confirm']:
            raise Warning(_("Inventory must be in the Draft or Confirmed state."))
        if self.barcode:
            stage_scan_obj = self.env['stock.inventory.stage.line']
            phrase = self.barcode
            products = self.env['product.product'].search([
                ('barcode', 'ilike', phrase)
            ])
            lines = self.line_ids.ids
            if products:
                product = products[0]

                # Search of lines with current product
                line_with_product_exist = self.line_ids.filtered(lambda x: x.product_id.id == product.id)

                if line_with_product_exist:
                    stage_line = line_with_product_exist[0]
                    stage_line.qty += 1
                else:
                    stage_line = stage_scan_obj.create({
                        'stage_id': self._origin.id,
                        'product_id': product.id,
                        'qty': 1,
                    })
                    lines.append(stage_line.id)

                self.line_ids = [(6, 0, lines)]
                self.env.user.notify_info(
                    _(u'Product added: {}').format(product.name),
                )
            else:
                self.env.user.notify_warning(
                    _(u'Barcode is not found: {}').format(self.barcode),
                    sticky=True,
                )
            self.barcode = ''


    @api.multi
    def action_stage_done(self):
        self.write({'state': 'done'})
