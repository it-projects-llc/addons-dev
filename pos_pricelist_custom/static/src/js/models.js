odoo.define('pos_pricelist_custom.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var utils = require('web.utils');

    var round_pr = utils.round_precision;
    var round_di = utils.round_decimals;

    models.load_fields('product.pricelist',['pos_discount_policy']);

    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        get_pricelist_by_id: function(id) {
            return this.pricelists.find(function(pricelist) {
                return pricelist.id === id;
            });
        }
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        set_pricelist: function (pricelist) {
            var self = this;
            var lines_to_recompute = _.filter(this.get_orderlines(), function (line) {
                return ! line.price_manually_set;
            });
            _.each(lines_to_recompute, function (line) {
                line.pricelist = pricelist;
                line.show_original_unit_price = false;
                if (line.pricelist.id !== self.pricelist.id) {
                    line.set_discount(0);
                }
            });
            _super_order.set_pricelist.apply(this, arguments);
            if (pricelist.pos_discount_policy === "without_discount") {
                _.each(lines_to_recompute, function (line) {
                    line.show_original_unit_price = true;
                    var discount = line.calc_discount(pricelist);
                    line.set_unit_price(line.original_unit_price);
                    self.fix_tax_included_price(line);
                    line.set_discount(discount);
                });
            }
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options) {
            this.pricelist = {};
            _super_orderline.initialize.apply(this, arguments);
            this.original_unit_price = this.product.lst_price;
            var pricelist = this.order.pricelist;
            if (this.pricelist && this.pricelist.id) {
                pricelist = this.pricelist;
            }
            if (!options.price && this.order.pricelist && pricelist.pos_discount_policy === "without_discount") {
                this.show_original_unit_price = true;
                var discount = this.calc_discount(pricelist);
                this.set_unit_price(this.original_unit_price);
                this.order.fix_tax_included_price(this);
                this.set_discount(discount);
            } else {
                this.show_original_unit_price = false;
            }
        },
        calc_discount: function(pricelist) {
            var discount_type = this.get_discount_type();
            if (discount_type === "percentage") {
                var percent = 0;
                var rounding = this.pos.currency.rounding;
                if (this.original_unit_price !== 0) {
                    var price = this.product.get_price(pricelist, this.get_quantity());
                    percent = round_pr(100.0 - (price * 100.0) / this.original_unit_price, rounding);
                }
                return percent;
            } else {
            //    TODO: calc for another discounts
                return 0;
            }
        },
        get_display_original_price: function () {
            if (this.pos.config.iface_tax_included === 'total') {
                return this.get_original_price_with_tax();
            } else {
                return this.get_original_price();
            }
        },
        get_original_price_with_tax: function(){
            return this.get_all_prices().OriginalPriceWithTax;
        },
        get_original_unit_price: function() {
            var digits = this.pos.dp['Product Price'];
            return  parseFloat(round_di(this.original_unit_price || 0, digits).toFixed(digits));
        },
        get_original_price:    function(){
            var rounding = this.pos.currency.rounding;
            var original_unit_price = this.get_original_unit_price();
            return round_pr(original_unit_price * this.get_quantity(), rounding);
        },
        get_all_prices: function() {
            var res = _super_orderline.get_all_prices.call(this);
            var price_unit = this.get_original_unit_price();
            var product =  this.get_product();
            var taxes_ids = product.taxes_id;
            var taxes =  this.pos.taxes;
            var product_taxes = [];
            _(taxes_ids).each(function(el){
                product_taxes.push(_.detect(taxes, function(t){
                    return t.id === el;
                }));
            });
            var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
            res.OriginalPriceWithTax = all_taxes.total_included;
            res.OriginalPriceWithoutTax = all_taxes.total_excluded;
            return res;
        },
        get_discount_type: function() {
            return "percentage";
        },
        set_default_pricelist: function() {
            var pricelist = this.pos.default_pricelist;
            var order = this.pos.get_order();
            this.set_unit_price(this.product.get_price(pricelist, this.get_quantity()));
            order.fix_tax_included_price(this);
            if (pricelist.pos_discount_policy === "without_discount") {
                this.show_original_unit_price = true;
                var discount = this.calc_discount(pricelist);
                this.set_unit_price(this.original_unit_price);
                order.fix_tax_included_price(this);
                this.set_discount(discount);
            } else {
                this.show_original_unit_price = false;
                this.set_discount(0);
            }
            this.pricelist = pricelist;
            this.trigger('change', this);
        },
        init_from_JSON: function(json) {
            _super_orderline.init_from_JSON.apply(this, arguments);
            this.pricelist = json.pricelist;
            this.original_unit_price = json.original_unit_price;
            this.show_original_unit_price = json.show_original_unit_price;
        },
        export_as_JSON:function(){
            var res = _super_orderline.export_as_JSON.apply(this, arguments);
            res.pricelist = this.pricelist;
            res.original_unit_price = this.original_unit_price;
            res.show_original_unit_price = this.show_original_unit_price;
            return res;
        },
    });
    return models;
});
