/* Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_orders_history_return.screens', function (require) {
    "use strict";

    var core = require('web.core');
    var screens = require('pos_orders_history.screens');
    var models = require('pos_orders_history.models');
    var QWeb = core.qweb;
    var _t = core._t;


    screens.OrdersHistoryScreenWidget.include({
        show: function () {
            var self = this;
            this._super();
            if (this.pos.config.return_orders) {
                this.$('.actions.oe_hidden').removeClass('oe_hidden');
                this.$('.button.return').unbind('click');
                this.$('.button.return').click(function (e) {
                    var parent = $(this).parents('.order-line');
                    var id = parseInt(parent.data('id'));
                    self.click_return_order_by_id(id);
                });
            }
        },
        click_return_order_by_id: function(id) {
            var self = this;
            var order = self.pos.db.orders_history_by_id[id];
            var lines = [];
            order.lines.forEach(function(line_id) {
                lines.push(self.pos.db.line_by_id[line_id]);
            });
            var products = [];
            lines.forEach(function(line) {
                var product = self.pos.db.get_product_by_id(line.product_id[0]);
                products.push(product);
            });
            if (products.length > 0) {
                // create new order for return
                var uid = order.pos_reference.split(' ')[1];
                var split_sequence_number = uid.split('-');
                var sequence_number = split_sequence_number[split_sequence_number.length - 1];

                var json = _.extend({}, order);
                json.uid = uid;
                json.sequence_number = Number(sequence_number);
                json.lines = [];
                json.statement_ids = [];
                json.mode = "return";
                json.return_lines = lines;

                var options = _.extend({pos: this.pos}, {json: json});
                order = new models.Order({}, options);

                this.pos.get('orders').add(order);
                this.pos.gui.back();
                this.pos.set_order(order);
                this.pos.chrome.screens.products.product_list_widget.set_product_list(products);
            } else {
                this.pos.gui.show_popup('error', _t('Order Is Empty'));
            }
        },
    });

    screens.ProductCategoriesWidget.include({
        renderElement: function() {
            this._super();
            var self = this;
            var order = this.pos.get_order();
            if (order.get_mode() === "return") {
                var products = [];
                order.return_lines.forEach(function(line) {
                    var product = self.pos.db.get_product_by_id(line.product_id[0]);
                    product.max_return_qty = line.qty;
                    products.push(product);
                });
                this.product_list_widget.set_product_list(products);
            }
        }
    });

    screens.ProductListWidget.include({
        render_product: function(product){
            var cached = this._super(product);
            var order = this.pos.get_order();
            var el = $(cached).find('.max-return-qty');
            if (el.length) {
                el.remove();
            }
            if (order.get_mode() === "return" && product.max_return_qty) {
                var current_return_qty = order.get_current_product_return_qty(product);
                var qty = product.max_return_qty - current_return_qty;
                $(cached).find('.product-img').append('<div class="max-return-qty">' + qty + '</div>');
            }
            return cached;
        },
    });

    return screens;
});
