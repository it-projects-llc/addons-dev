odoo.define('pos_discount_absolute', function (require) {
"use strict";

    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.gui');
    var Widget = require('web.Widget');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var PopupWidget = require('point_of_sale.popups');
    var core = require('web.core');
    var screens = require('point_of_sale.screens');

    var QWeb = core.qweb;


    PosBaseWidget.include({
        init:function(parent,options){
            var self = this;
            this._super(parent,options);
            if (this.gui && this.gui.screen_instances.products &&
                this.gui.screen_instances.products.action_buttons.discount && this.pos.config.discount_abs_enabled) {
                var disc_widget = this.gui.screen_instances.products.action_buttons.discount;
                disc_widget.button_click = function () {
                    self.gui.show_popup('number', {
                        'title': 'Absolute Discount',
                        'value': self.pos.config.discount_abs_value,
                        'confirm': function (val) {
                            self.apply_discount(val);
                            self.pos.config.discount_abs_value = val;
                        },
                    });
                };
            }
        },
        apply_discount: function(val) {
            var order = this.pos.get_order();
            var lines = order.get_orderlines();
            var product = this.pos.db.get_product_by_id(this.pos.config.discount_product_id[0]);
            // Remove existing discounts
            lines.forEach( function(line){
                if (line.get_product() === product){
                    order.remove_orderline(line);
                }
            });
            // Add discount
            if (val != 0){
                if (this.pos.config.discount_abs_type){
                    var discount = - Math.min(val, order.get_total_with_tax());
                    order.add_product(product, { price: discount });
                } else {
                    var discount = - val / 100.0 * order.get_total_with_tax();
                    if( discount < 0 ){
                        order.add_product(product, { price: discount });
                    }
                }
            }
        },

    });

    PopupWidget.include({
        show: function (options) {
            var self = this;
            this._super(options);
            this.popup_abs_discount = false;
            if (this.pos.config.discount_abs_enabled) {
                self.popup_abs_discount = true;
                self.events["click .absolute.button"] = "click_absolute_discount";
                self.events["click .percentage.button"] = "click_percentage_discount";
            }
        },
        click_absolute_discount: function() {
            var self = this;
            this.pos.config.discount_abs_type = true;
            this.renderElement();
        },
        click_percentage_discount: function() {
            var self = this;
            this.pos.config.discount_abs_type = false;
            this.renderElement();
        },
        renderElement: function(){
            this._super();
            if (this.popup_abs_discount) {
                this.$('.popup.popup-number').addClass("popup-abs-discount");
                var header_buttons_html = QWeb.render('abs_disc_widget_header_buttons',{widget: this});
                var node = document.getElementsByClassName("popup-input value active")[0];
                var div = document.createElement('div');
                div.innerHTML = header_buttons_html;
                div.className = "header";
                node.parentElement.insertBefore(div, node);
                var header_title = node.parentElement.getElementsByClassName("title")[0];
                var text = this.pos.config.discount_abs_type && "Absolute Discount" || "Discount Percentage"
                header_title.innerText = text;
            }
        },
    });

    screens.OrderWidget.include({
        update_summary: function(){
            var order = this.pos.get('selectedOrder');
            this._super();
            if (!order.get_orderlines().length) {
                return;
            }
            var total = order ? order.get_total_with_tax() : 0;
            total = total != 0 && total || 'FREE'
            this.el.querySelector('.summary .total > .value').textContent = this.format_currency(total);
        },

    });

    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        initialize: function(){
            var self = this;
            OrderlineSuper.prototype.initialize.apply(this, arguments);
        },
        set_discount: function(discount){
            var previous_disc = this.get_discount() || 0;
            var new_disc = discount === "" && "0" || parseFloat(discount) + previous_disc*10;
            discount = new_disc.toString();

            OrderlineSuper.prototype.set_discount.apply(this, [discount]);

            var products_widgets = this.pos.gui.screen_instances.products;
            var discount_is_set = _.find(this.order.get_orderlines(), function(line){return line.price < 0 })
            if ( discount_is_set && this.pos.config.discount_abs_enabled && products_widgets &&
            products_widgets.action_buttons && products_widgets.action_buttons.discount){
                var disc_widget = products_widgets.action_buttons.discount;
                disc_widget.apply_discount(this.pos.config.discount_abs_value);
                this.order.select_orderline(this);
                this.pos.gui.current_screen.numpad.state.set({mode: "discount"});
            }
        },
        get_display_price: function(){
            if (this.pos.config.iface_tax_included) {
                return this.get_price_with_tax() === 0 && "FREE" || this.get_price_with_tax();
            } else {
                return this.get_base_price() === 0 && "FREE" || this.get_base_price();
            }
        },
    });

});
