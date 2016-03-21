from openerp import models

class ProductAttributeSaaS(models.Model):
    _inherit = "product.attribute"


    def _get_codes(self):
        res = super(ProductAttributeSaaS, self)._get_codes()
        return res + [('sale_contract_hours.prepaid_service_units', 'Prepaid Service Units')]
