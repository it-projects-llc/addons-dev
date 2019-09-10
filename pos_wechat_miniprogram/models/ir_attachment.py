from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def check(self, mode, values=None):
        if self:
            res = self.filtered(lambda record: record.res_model not in ["product.template", "product.product"])
        if values and values.get("res_model") in ["product.template", "product.product"]:
            values = None
        super(IrAttachment, res).check(mode, values)
