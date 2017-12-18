odoo.define('pos_pricelist_absolute_discount.models', function(require){

    var models = require('pos_pricelist.models');
    require('pos_absolute_discount.models');
    var utils = require('web.utils');

    var round_pr = utils.round_precision;
    var round_di = utils.round_decimals;

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        calc_discount_percent: function(product_price, current_price) {
            if (this.active_pricelist_item && this.active_pricelist_item['fixed_price']) {
                this.set_absolute_discount(product_price - current_price);
                return false;
            }
            return _super_orderline.calc_discount_percent.call(this, product_price, current_price);
        },
        get_all_prices: function() {
            var res = _super_orderline.get_all_prices.apply(this, arguments);
            if (this.get_absolute_discount()) {
                var base = this.get_base_price();
                var totalTax = base;
                var totalNoTax = base;
                var taxtotal = 0;
                var taxdetail = {};
                var product_taxes = this.get_applicable_taxes_for_orderline();
                var price_unit = this.get_unit_price() - (this.get_absolute_discount() / this.get_quantity());
                var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
                _(all_taxes.taxes).each(function (tax) {
                    if (tax.price_include) {
                        totalNoTax -= tax.amount;
                    } else {
                        totalTax += tax.amount;
                    }
                    taxtotal += tax.amount;
                    taxdetail[tax.id] = tax.amount;
                });
                totalNoTax = round_pr(totalNoTax, this.pos.currency.rounding);
                res.priceWithTax = all_taxes.total_included;
                res.priceWithoutTax = all_taxes.total_excluded;
                res.tax = taxtotal;
                res.taxDetails = taxdetail;
            }
            return res;
        }
    });
});
