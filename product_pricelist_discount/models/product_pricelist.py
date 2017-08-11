# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools, _
from itertools import chain
from odoo.exceptions import UserError


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    # base product or category
    base_pos_category_ids = fields.Many2many('pos.category', 'base_pos_category_rel')
    promotional_product_tmpl_id = fields.Many2one('product.template', 'Product', ondelete='cascade')

    # promotional product or category (discount)
    promotional_product_id = fields.Many2one("product.product", "Promotional Product", ondelete="cascade", help='Promotional Product')
    promotional_pos_category_ids = fields.Many2many('pos.category', 'promotional_pos_category_rel', help='Promotional POS Category')
    promotional_product_quantity = fields.Integer("Quantity", default=1, help="Promotional Product Quantity")
    quantity_included = fields.Boolean("Quantity Included", default=False, help="Select if the Promotional Product Quantity is included in the minimum quantity (Only if the promo product coincides with the base product)")
    status_quantity_included = fields.Boolean(compute="_compute_status_quantity_included")
    cumulative_quantity = fields.Boolean("Cumulative Quantity", default=True, help="Select if you want to consider the sum of the quantities of all products in the rule and repeat rule")

    # total order discount
    amount_order_total = fields.Float("Total Amount", help="For POS. If more than total amount, then a discount is applied", ondelete='cascade')
    total_discount_product = fields.Many2one('product.product', string='Total Discount Product', domain="[('available_in_pos', '=', True)]", help='The product used to model the discount')

    # discount type
    applied_on = fields.Selection([
        ('5_amount_order_total', 'Order Total'),
        ('4_promotional_product', 'Promotional Product'),
        ('3_global', 'Global'),
        ('2_product_category', ' Product Category'),
        ('1_product', 'Product'),
        ('0_product_variant', 'Product Variant')], "Apply On",
        default='3_global', required=True,
        help='Pricelist Item applicable on selected option')

    promotional_type = fields.Selection([
        ('1_product', 'Product'),
        ('0_category', 'Category')], "Promotional Type",
        default='1_product', required=True,
        help='Promotional applicable on selected option')

    base_type = fields.Selection([
        ('1_product', 'Product'),
        ('0_category', 'Category')], "Type",
        default='1_product', required=True,
        help='Type applicable on selected option')

    @api.depends('promotional_product_id', 'promotional_product_tmpl_id')
    def _compute_status_quantity_included(self):
        if self.promotional_product_id and self.promotional_product_tmpl_id and self.promotional_product_id.id == self.promotional_product_tmpl_id.product_variant_id.id:
            self.status_quantity_included = True
        else:
            self.status_quantity_included = False

    @api.one
    @api.depends('promotional_product_id', 'promotional_product_tmpl_id', 'promotional_pos_category_ids',
                 'base_pos_category_ids', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price',
                 'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge', 'quantity_included',
                 'cumulative_quantity')
    def _get_pricelist_item_name_price(self):
        super(PricelistItem, self)._get_pricelist_item_name_price()
        promo_name = ''
        if self.cumulative_quantity:
            cumulative_quantity = _(", With Cumulative Quantity")
        else:
            cumulative_quantity = _(", Without Cumulative Quantity")
        if self.base_pos_category_ids:
            base_categories_name = ''
            for r in self.base_pos_category_ids:
                base_categories_name = base_categories_name + r.name + ', '
                base_categories_name = base_categories_name[:-2]
            promo_name = _("Category: %s, " % base_categories_name)
        elif self.promotional_product_tmpl_id:
            promo_name = _("Product: %s, " % self.promotional_product_tmpl_id.name)
        if self.promotional_product_id:
            promo_qty_included = ''
            if self.quantity_included:
                promo_qty_included = _("included in the Min. Quantity")
            promo_name = promo_name + _("Promotional Product: %s " % self.promotional_product_id.name) + promo_qty_included + cumulative_quantity
        elif self.promotional_pos_category_ids:
            promo_categories_name = ''
            for r in self.promotional_pos_category_ids:
                promo_categories_name = promo_categories_name + r.name + ', '
            promo_categories_name = promo_categories_name[:-2]
            promo_name = promo_name + _("Promotional Category: %s" % promo_categories_name) + cumulative_quantity
        if promo_name:
            self.name = promo_name
        if self.amount_order_total > 0:
            self.name = _("Total Amount: %s" % self.amount_order_total)

    @api.onchange('applied_on', 'promotional_type', 'base_type', 'min_quantity', 'status_quantity_included')
    def _onchange_applied_on(self):
        if self.promotional_type == "1_product":
            self.promotional_pos_category_ids = False
        elif self.promotional_type == "0_category":
            self.promotional_product_id = False

        if self.base_type == "1_product":
            self.base_pos_category_ids = False
        elif self.base_type == "0_category":
            self.promotional_product_tmpl_id = False

        if not self.status_quantity_included:
            self.quantity_included = False
        if self.applied_on == '5_amount_order_total':
            self.categ_id = False
            self.product_tmpl_id = False
            self.product_id = False
            self.min_quantity = False
        if self.applied_on != '4_promotional_product':
            self.promotional_product_id = False
            self.promotional_product_tmpl_id = False
            self.promotional_product_quantity = 0
            self.promotional_pos_category_ids = False
            self.quantity_included = False
            self.base_pos_category_ids = False
        elif self.applied_on != '5_amount_order_total':
            self.amount_order_total = 0
            self.total_discount_product = False
        else:
            super(PricelistItem, self)._onchange_applied_on()

class Pricelist(models.Model):
    _inherit = "product.pricelist"

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        If date in context: Date of the pricelist (%Y-%m-%d)

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date', fields.Date.today())
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            product_ids = [item[0].id for item in products_qty_partner]
            products = self.env['product.product'].with_context(uom=uom_id).browse(product_ids)
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        self._cr.execute(
            'SELECT item.id '
            'FROM product_pricelist_item AS item '
            'LEFT JOIN product_category AS categ '
            'ON item.categ_id = categ.id '
            'WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))'
            'AND (item.product_id IS NULL OR item.product_id = any(%s))'
            'AND (item.categ_id IS NULL OR item.categ_id = any(%s)) '
            'AND (item.pricelist_id = %s) '
            'AND (item.date_start IS NULL OR item.date_start<=%s) '
            'AND (item.date_end IS NULL OR item.date_end>=%s)'
            'ORDER BY item.applied_on, item.min_quantity desc, categ.parent_left desc',
            (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))

        item_ids = [x[0] for x in self._cr.fetchall()]
        items = self.env['product.pricelist.item'].browse(item_ids)
        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['product.uom'].browse([self._context['uom']])._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            price = product.price_compute('list_price')[product.id]

            price_uom = self.env['product.uom'].browse([qty_uom_id])
            for rule in items:
                if rule.applied_on == "5_amount_order_total" and rule.amount_order_total > 0:
                    continue
                if rule.applied_on == "4_promotional_product":
                    continue
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)])[product.id][0]  # TDE: 0 = price, 1 = rule
                    price = rule.base_pricelist_id.currency_id.compute(price_tmp, self.currency_id, round=False)
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]

                convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))

                if price is not False:
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'percentage':
                        price = (price - (price * (rule.percent_price / 100))) or 0.0
                    else:
                        # complete formula
                        price_limit = price
                        price = (price - (price * (rule.price_discount / 100))) or 0.0
                        if rule.price_round:
                            price = tools.float_round(price, precision_rounding=rule.price_round)

                        if rule.price_surcharge:
                            price_surcharge = convert_to_price_uom(rule.price_surcharge)
                            price += price_surcharge

                        if rule.price_min_margin:
                            price_min_margin = convert_to_price_uom(rule.price_min_margin)
                            price = max(price, price_limit + price_min_margin)

                        if rule.price_max_margin:
                            price_max_margin = convert_to_price_uom(rule.price_max_margin)
                            price = min(price, price_limit + price_max_margin)
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                price = product.currency_id.compute(price, self.currency_id, round=False)

            results[product.id] = (price, suitable_rule and suitable_rule.id or False)

        return results
