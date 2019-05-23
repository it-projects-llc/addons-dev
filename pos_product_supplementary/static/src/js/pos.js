/* Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */

odoo.define('pos_product_supplementary.pos', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var PosDb = require('point_of_sale.DB');
    var screens = require('point_of_sale.screens');
    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');

    models.load_fields('product.product', ['is_supplementary_product', 'supplementary_product_child_ids',
                                           'available_in_pos', 'name']);

    models.load_models([{
        model: 'product.product',
        fields: function(self) {
            var product_model = _.find(self.models, function(m){
                return m.model === 'product.product';
            });
            return product_model.fields;
        },
//        condition: function(self) {
//            return self.config.supplementary_products;
//        },
        domain: [['is_supplementary_product','=',true]],
        loaded: function(self, products){
            if (!products) {
                return;
            }
            var product_model = _.find(self.models, function(m){
                return m.model === 'product.product';
            });
            return product_model.loaded(self, products);
        },
    }], {'after':"product.product"});

    PosDb.include({
        get_supplementary_products_by_parent_id: function(pid) {
            var self = this;
            var product = this.get_product_by_id(pid);
            var products = [];
            _.each(product.supplementary_product_child_ids, function(pr_id) {
                products.push(self.get_product_by_id(pr_id));
            });
            return products;
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({

        get_supplementary_products: function() {
            return this.pos.db.get_supplementary_products_by_parent_id(this.product.id);
        },

        get_supplementary_orderlines: function() {
            var lines = [];
            var order = this.order;
            _.each(this.supplementary_line_ids, function(lid){
                lines.push(order.get_orderline(lid));
            });
            return lines;
        },

        hide_orderline: function() {
            $(this.node).hide();
        },

        get_total_for_supplementary_lines: function() {
            var self = this;
            var lines = this.supplementary_line_ids;
            if (!lines.length) {
                return false;
            }
            return _.chain(lines)
                .map(function(l){
                    var ol = self.order.get_orderline(l);
                    if (!ol) {
                        return 0;
                    }
                    return ol.get_display_price();
                })
                .reduce(function(memo, num){
                    return memo + num;
                }, 0).value();
        },

        get_display_price: function(){
            var result = _super_orderline.get_display_price.apply(this,arguments);
            if(this.supplementary_line_ids && this.supplementary_line_ids.length){
                return this.get_total_for_supplementary_lines() + result;
            }
            return result;
        },

        export_as_JSON: function() {
            var result = _super_orderline.export_as_JSON.apply(this,arguments);
            if (this.parented_orderline){
                result.parented_orderline = this.parented_orderline;
            }
            if (this.supplementary_line_ids){
                result.supplementary_line_ids = this.supplementary_line_ids;
            }
            return result;
        },

        init_from_JSON: function(json) {
            var result = _super_orderline.init_from_JSON.apply(this,arguments);
            if (json.parented_orderline){
                this.parented_orderline = json.parented_orderline;
            }
            if (json.supplementary_line_ids){
                this.supplementary_line_ids = json.supplementary_line_ids;
            }
            return result;
        },

        check_for_supplementary_and_repeat_for_them: function(func, obj, args) {
            if (obj.supplementary_line_ids && obj.supplementary_line_ids.length) {
                _.each(obj.get_supplementary_orderlines(), function(line){
                    func.apply(line, args);
                });
            }
        },

//        set_quantity: function(quantity, keep_price){
//            var super_method = _super_orderline.set_quantity;
//            this.check_for_supplementary_and_repeat_for_them(super_method, this, arguments);
//            super_method.apply(this, arguments);
//        },

        set_discount: function(discount){
            var super_method = _super_orderline.set_discount;
            this.check_for_supplementary_and_repeat_for_them(super_method, this, arguments);
            super_method.apply(this, arguments);
        },

    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({

        add_product: function(product, options) {
            var self = this;
            if (!this.pos.config.supplementary_products) {
                return _super_order.add_product.apply(this,arguments);
            }

            if (product && product.supplementary_product_child_ids && product.supplementary_product_child_ids.length) {
                options = options || {};
                var supplementary_line_ids = [];
                _.each(this.pos.db.get_supplementary_products_by_parent_id(product.id), function(p) {
                    self.add_product(p, {quantity:0, merge:false,});
                    supplementary_line_ids.push(self.get_last_orderline().id);
                });
                _super_order.add_product.apply(this, [product, _.extend(options, {merge: false,})]);
                var parented_orderline = self.get_last_orderline();
                parented_orderline.supplementary_line_ids = supplementary_line_ids;
                _.each(parented_orderline.get_supplementary_orderlines(), function(l){
                    l.parented_orderline = parented_orderline.id;
                });
                parented_orderline.set_quantity(1);
                self.pos.gui.screen_instances.products.order_widget.rerender_orderline(parented_orderline);
            } else {
                _super_order.add_product.apply(this,arguments);
            }
        },

        select_orderline: function(line){
            if(line && line.parented_orderline){
                line.hide_orderline();
                line = this.get_orderline(line.parented_orderline);
            }
            return _super_order.select_orderline.apply(this,arguments);
        },
    });

    screens.OrderWidget.include({

        rerender_orderline: function(order_line) {
            this._super(order_line);
            if (order_line.parented_orderline) {
                order_line.hide_orderline();
            }
            if (order_line.supplementary_line_ids && order_line.supplementary_line_ids.length) {
                var self = this;
                _.each(order_line.get_supplementary_orderlines(), function(l){
                    self.rerender_orderline(l);
                });
            }
        },

        render_orderline: function(orderline){
            var node = this._super(orderline);
            if (orderline.parented_orderline) {
                $(node).hide();
            }
            return node;
        },
    });

    var SupplementaryButton = screens.ActionButtonWidget.extend({
        template: 'SupplementaryButton',

        button_click: function(){
            var self = this;
            var selected_orderline = this.pos.get_order().get_selected_orderline();
            if (!selected_orderline) {
                return;
            }
            var line_ids = selected_orderline.supplementary_line_ids;
            if (!line_ids || !line_ids.length){
                return;
            }
            var values = [];
            _.each(line_ids, function(id) {
                values.push(self.pos.get_order().get_orderline(id));
            });
            this.gui.show_popup('supplementary',{
                'title': 'Supplementary Products',
                'list': values,
            });
        },
    });

    screens.define_action_button({
        'name': 'supplementary_button',
        'widget': SupplementaryButton,
        'condition': function () {
            return this.pos.config.supplementary_products;
        },
    });

    var SupplementaryPopupWidget = PopupWidget.extend({
        template: 'SupplementaryPopupWidget',
        events: _.chain({})
            .extend(PopupWidget.prototype.events, {'click .selection-item .name': 'click_item',})
            // we get rid of 'click .selection-item' because otherwise clicking on input triggers the handler for line
            .omit('click .selection-item').value(),

        show: function(options){
            var self = this;
            options = options || {};
            this._super(options);

            this.list = options.list || [];
            this.is_selected = options.is_selected || function (item) {
                return false;
            };
            this.renderElement();
            this.updated_lines = [];
        },

        click_confirm: function(){
            this.apply_qty_updates();
            this.gui.close_popup();
        },

        apply_qty_updates: function() {
            var self = this;
            var lines = this.$el.find('.supplementary_product_line .supp_qty_input input');
            var order = this.pos.get_order();
            _.each(lines, function(l){
                var olid = parseInt(l.getAttribute('olid') || 0);
                var qty = parseInt(l.value) || 0;
                order.get_orderline(olid).set_quantity(qty);
            });
            this.rerender_orderline(this.list[0].parented_orderline);
        },

        click_item: function(event) {
            var olid = parseInt(event.target.parentElement.parentElement.getAttribute('olid'));
            var orderline = this.pos.get_order().get_orderline(olid);
            orderline.set_quantity(orderline.quantity + 1);
            this.gui.close_popup();
            this.rerender_orderline(orderline.parented_orderline);
        },

        rerender_orderline: function(olid) {
            var orderline = this.pos.get_order().get_orderline(olid);
            this.pos.chrome.screens.products.order_widget.rerender_orderline(orderline);
        },

    });
    gui.define_popup({name:'supplementary', widget: SupplementaryPopupWidget});

    screens.ProductListWidget.include({
        set_product_list: function(product_list){
            product_list = _.filter(product_list, function(p){
                return p.available_in_pos;
            });
            if (this.pos.config.hide_supplementary_products) {
                product_list = _.filter(product_list, function(p){
                    return !p.is_supplementary_product;
                });
            }
            return this._super(product_list);
        },

    });

     screens.PaymentScreenWidget.include({

        finalize_validation: function() {
            var self = this;
            var order = this.pos.get_order(),
            orderlines = order.get_orderlines();
            // removes excessive child orderlines. Big refactoring is needed to avoid this overriding / behavior
            var zero_qty_supplementary_orderlines = _.filter(orderlines, function(ol){
                return ol.parented_orderline && ol.quantity === 0;
            });
            _.each(zero_qty_supplementary_orderlines, function(ol){
                order.remove_orderline(ol);
            })
            this._super();
        },
    });

});
