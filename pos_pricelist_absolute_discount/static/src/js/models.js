odoo.define('pos_pricelist_absolute_discount.models', function(require){

    var models = require('pos_pricelist.models');
    require('pos_absolute_discount.models');
    var utils = require('web.utils');
    var screens = require('point_of_sale.screens');

    var round_pr = utils.round_precision;
    var round_di = utils.round_decimals;


    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes, options){
            _super_order.initialize.apply(this, arguments);
            this.set_active_pricelist();
        },
        set_client: function(client){
            _super_order.set_client.apply(this,arguments);
            this.set_active_pricelist();
        },
        set_active_pricelist: function() {
            var partner = this.get_client() || false;
            if (partner && partner.property_product_pricelist) {
                this.current_price_list = partner.property_product_pricelist;
            } else {
                this.current_price_list = this.pos.config.pricelist_id;
            }
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options){
            _super_orderline.initialize.apply(this, arguments);
            this.check_pricelist();
        },
        set_quantity: function (quantity) {
            _super_orderline.set_quantity.apply(this, arguments);
            this.check_pricelist();
        },
        check_pricelist: function() {
            var order = this.pos.get_order() || this.order;
            if (order && this.product) {
                var pricelist_id = order.current_price_list[0];
                var partner = order.get_client() || false;
                if (partner && partner.property_product_pricelist && this.default_pricelist) {
                    pricelist_id = this.pos.config.pricelist_id[0];
                    partner = false;
                }
                this.set_discount(0);
                if (this.pos.db.pricelist_by_id[pricelist_id].pos_discount_policy === "without_discount") {
                    var old_price = this.product.list_price;
                    var current_price = this.pos.pricelist_engine.compute_price_all(
                        this.pos.db, this.product, partner, this.quantity
                    );
                    this.set_unit_price(old_price);
                    if (old_price != current_price) {
                        this.change_discount(old_price, current_price);
                    }
                    this.trigger('change', this);
                }
            }
        },
        change_discount: function(old_price, current_price) {
            var discount_type = this.get_discount_type();
            if (discount_type === "fixed") {
                this.set_absolute_discount(this.calc_absolute_discount_value(old_price, current_price));
            } else {
                this.set_discount(this.calc_discount_percent(old_price, current_price));
            }
        },
        calc_discount_percent: function(old_price, current_price) {
            var percent = 0;
            var rounding = this.pos.currency.rounding;
            if (old_price !== 0) {
                percent = round_pr(100.0 - (current_price * 100.0) / old_price, rounding);
            }
            return percent;
        },
        calc_absolute_discount_value: function(old_price, current_price) {
            return old_price - current_price;
        },
        get_discount_type: function() {
            var rules = this.get_active_pricelist_items_by_product();
            var type = "percentage";
            if (rules.length) {
                type = rules[0].compute_price;
            }
            return type;
        },
        get_active_pricelist_items_by_product: function() {
            var self = this;
            var order = this.pos.get_order() || this.order;
            if (order) {
                var pricelist_id = order.current_price_list[0];
                var partner = order.get_client() || false;
                if (partner && partner.property_product_pricelist && this.default_pricelist) {
                    pricelist_id = this.pos.config.pricelist_id[0];
                }
                var rules = this.pos.pricelist_engine.get_rule_items_by_pricelist_id(pricelist_id);
                return rules.filter(function(rule) {
                    return rule.min_quantity <= self.quantity &&
                    ((rule.product_tmpl_id && rule.product_tmpl_id[0] === self.product.product_tmpl_id || rule.applied_on === "3_global"));
                });
            }
        },
        set_default_pricelist: function() {
            _super_orderline.set_default_pricelist.apply(this, arguments);
            this.default_pricelist = true;
            this.check_pricelist();
        },
    });

    var _super_pricelistengine = models.PricelistEngine.prototype;
    models.PricelistEngine = models.PricelistEngine.extend({
        get_rule_items_by_pricelist_id: function(id) {
            return this.pos.db.pricelist_item_sorted.filter(function(item) {
                return item.pricelist_id[0] === id;
            });
        },
        update_products_ui: function (partner) {
            var db = this.db;
            var current_price_list = false;
            if (partner && partner.property_product_pricelist) {
                current_price_list = partner.property_product_pricelist;
            } else {
                current_price_list = this.pos.config.pricelist_id;
            }

	        var product_list_ui = $('.product-list .product');
            for (var i = 0, len = product_list_ui.length; i < len; i++) {
                var product_ui = product_list_ui[i];
                var product_id = $(product_ui).data('product-id');
                var product = $.extend({}, db.get_product_by_id(product_id));
                var rules = db.find_product_rules(product);
                var quantities = [];
                quantities.push(1);
                for (var j = 0; j < rules.length; j++) {
                    if ($.inArray(rules[j].min_quantity, quantities) === -1) {
                        quantities.push(rules[j].min_quantity);
                    }
                }
                quantities = quantities.sort();
                var prices_displayed = '';
                for (var k = 0; k < quantities.length; k++) {
                    var qty = quantities[k];
                    var price = this.compute_price_all(
                        db, product, partner, qty
                    );
                    if (price !== false) {
                        if (this.pos.config.iface_tax_included) {
                            var prices = this.simulate_price(
                                product, partner, price, qty
                            );
                            price = prices['priceWithTax']
                        }
                        if (this.pos.db.pricelist_by_id[current_price_list[0]].pos_discount_policy === "without_discount") {
                            price = product.list_price;
                        }
                        price = round_di(parseFloat(price)
                            || 0, this.pos.dp['Product Price']);

                        var product_screen_widget = new screens.ProductScreenWidget(this, {});
                        price = product_screen_widget.format_currency(price);

                        if (k == 0) {
                            $(product_ui).find('.price-tag').html(price);
                        }
                        prices_displayed += qty
                            + 'x &#8594; ' + price + '<br/>';
                    }
                }
                if (prices_displayed != '') {
                    $(product_ui).find('.price-tag').attr(
                        'data-original-title', prices_displayed
                    );
                    $(product_ui).find('.price-tag').attr(
                        'data-toggle', 'tooltip'
                    );
                    $(product_ui).find('.price-tag').tooltip(
                        {delay: {show: 50, hide: 100}}
                    );
                }
            }
        },
        update_ticket: function (partner, orderLines) {
            _super_pricelistengine.update_ticket.apply(this, arguments);
            orderLines.forEach(function(line) {
                line.check_pricelist();
            });
        }
    });
});
