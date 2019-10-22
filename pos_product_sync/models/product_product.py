# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0.html).
from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def check_fields_to_send(self, vals):
        fields = self.env["ir.config_parameter"].sudo().get_param("pos_product_sync.product_sync_field_ids",
                                                                  default=False)
        if not fields:
            return False
        field_names = self.env['ir.model.fields'].browse([int(x) for x in fields.split(',')]).mapped('name')
        for name in field_names:
            if name in vals:
                return True
        return False

    @api.multi
    def write(self, vals):
        result = super(ProductProduct, self).write(vals)
        if self.check_fields_to_send(vals):
            img_vals = ['image', 'image_medium', 'image_small', 'image_variant']
            if any(val in img_vals for val in vals):
                self.send_field_updates(self.ids, action='update_image')
            else:
                self.send_field_updates(self.ids)
        return result

    @api.model
    def create(self, vals):
        product = super(ProductProduct, self).create(vals)
        if self.check_fields_to_send(vals):
            self.send_field_updates([product.id])
        return product

    @api.multi
    def unlink(self):
        res = super(ProductProduct, self).unlink()
        self.send_field_updates(self.ids, action='unlink')
        return res

    @api.model
    def send_field_updates(self, product_ids, action=''):
        channel_name = "pos_product_sync"
        data = {'message': 'update_product_fields', 'action': action, 'product_ids': product_ids}
        self.env['pos.config'].send_to_all_poses(channel_name, data)


class ProductChangeQuantity(models.TransientModel):
    _inherit = "stock.change.product.qty"

    def change_product_qty(self):
        res = super(ProductChangeQuantity, self).change_product_qty()
        product_ids = []
        for wizard in self:
            product_ids.append(wizard.product_id.id)
        self.env['product.product'].send_field_updates(product_ids)
        return res


class PosOrder(models.Model):

    _inherit = "pos.order"

    # Compatibility with pos_product_available
    def _process_order(self, pos_order):
        res = super(PosOrder, self)._process_order(pos_order)
        product_env = self.env['product.product']
        if product_env.check_fields_to_send("qty_available"):
            product_ids = [product[2]['product_id']
                           for product in pos_order['lines']
                           if product_env.browse(product[2]['product_id']).type == 'product']
            product_env.send_field_updates(product_ids)
        return res
