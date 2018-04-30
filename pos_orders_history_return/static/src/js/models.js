/* Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_orders_history_return.models', function (require) {
    "use strict";

    var models = require('pos_orders_history.models');

    var _super_pos_model = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        update_orders_history: function (orders) {
            if (!(orders instanceof Array)) {
                orders = [orders];
            }
            if (!this.config.show_returned_orders) {
                orders = orders.filter(function(order) {
                    return order.returned_order !== true;
                });
            }
            _super_pos_model.update_orders_history.call(this, orders);
        },
        get_returned_orders_by_pos_reference: function(reference) {
            var all_orders = this.db.pos_orders_history;
            return all_orders.filter(function(order){
                return order.returned_order && order.pos_reference === reference;
            });
        }
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function(product, options) {
            options = options || {};
            if (this.get_mode() === "return") {
                var current_return_qty = this.get_current_product_return_qty(product);
                var quantity = 1;
                if(options.quantity !== undefined) {
                    quantity = options.quantity;
                }
                if (current_return_qty + quantity <= product.max_return_qty)  {
                    _super_order.add_product.apply(this, arguments);
                    this.change_return_product_limit(product);
                }
            } else {
                _super_order.add_product.apply(this, arguments);
            }
        },
        get_current_product_return_qty: function(product) {
            var orderlines = this.get_orderlines();
            var product_orderlines = orderlines.filter(function(line) {
                return line.product.id === product.id;
            });
            var qty = 0;
            product_orderlines.forEach(function(line){
                qty += line.quantity;
            });
            if (qty < 0) {
                qty = -qty;
            }
            return qty;
        },
        change_return_product_limit: function(product) {
            var el = $('span[data-product-id="'+product.id+'"] .max-return-qty');
            var qty = this.get_current_product_return_qty(product);
            el.html(product.max_return_qty - qty);
        },
        export_as_JSON: function() {
            var data = _super_order.export_as_JSON.apply(this, arguments);
            data.return_lines = this.return_lines;
            return data;
        },
        init_from_JSON: function(json) {
            this.return_lines = json.return_lines;
            _super_order.init_from_JSON.call(this, json);
        }
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        set_quantity: function(quantity) {
            var order = this.pos.get_order();
            var old_quantity = String(quantity);
            if (order && order.get_mode() === "return" && quantity !== "remove") {
                var current_return_qty = this.order.get_current_product_return_qty(this.product);
                if (this.quantity) {
                    current_return_qty = current_return_qty + this.quantity;
                }
                if (quantity) {
                    if (current_return_qty + Number(quantity) <= this.product.max_return_qty) {
                        quantity = -quantity;
                    } else {
                        return;
                    }
                }
                _super_orderline.set_quantity.call(this, quantity);
                order.change_return_product_limit(this.product);
            } else {
                _super_orderline.set_quantity.call(this, quantity);
            }
        }
    });
});
