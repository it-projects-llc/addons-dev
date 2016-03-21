from openerp import models, fields


class ProductAttributeSaaS(models.Model):
    _inherit = "product.attribute"

    code = fields.Selection('_get_codes', string='Technical code')

    def _get_codes(self):
        # to be inherited
        return []


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    code_value = fields.Char('Technical value')
