odoo.define('pos_discount_absolute', function (require) {
"use strict";

    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.gui');
    var Widget = require('web.Widget');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var PopupWidget = require('point_of_sale.popups');
    var core = require('web.core');
    var screens = require('pos_discount_base.screens');
    var PosDiscountWidget = require('pos_discount.pos_discount');
    var QWeb = core.qweb;
    var _t = core._t;

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
            this.pos.discount_abs_type = true;
            this.renderElement("Absolute Discount");
        },
        click_percentage_discount: function() {
            this.pos.discount_abs_type = false;
            this.renderElement("Discount Percentage");
        },
        renderElement: function(options){
            if (options) {
                this.options.title = options;
            }
            this._super();
            if (this.popup_abs_discount) {
                this.$('.popup.popup-number').addClass("popup-abs-discount");
                var header_buttons_html = QWeb.render('abs_disc_widget_header_buttons',{widget: this});
                var node = $('.popup-abs-discount > .popup-input')[0];
                var div = document.createElement('div');
                div.innerHTML = header_buttons_html;
                div.className = "header";
                node.parentElement.insertBefore(div, node);
            }
        },
    });

    screens.OrderWidget.include({
        apply_discount: function(val) {
            var self = this;
            if (this.pos.discount_abs_type){
                this.apply_absolute_discount(val);
            } else {
                this._super(val);
            }
        },
        confirm_discount: function(val) {
            if (this.pos.discount_abs_type){
                this.apply_absolute_discount(val);
            } else {
                if (this.abs_disc_presence()) {
                    this.remove_abs_discount();
                    this._super(val);
                    this.apply_absolute_discount(this.pos.discount_abs_value);
                } else {
                    this._super(val);
                }
            }
        },
        apply_absolute_discount: function(val){
            this.pos.discount_abs_value = val;
            var order = this.pos.get_order();
            var abs_disc_product = this.pos.db.get_product_by_id(this.pos.config.discount_abs_product_id[0]);
            this.remove_abs_discount();
            var discount = - Math.min(val, order.get_total_with_tax());
            if (val !== 0){
                order.add_product(abs_disc_product, { price: discount });
            }
        },
        abs_disc_presence: function() {
            var presence = false;
            var lines = this.pos.get_order().get_orderlines();
            var abs_disc_product = this.pos.db.get_product_by_id(this.pos.config.discount_abs_product_id[0]);
            lines.forEach( function(line){
                if (line.get_product() === abs_disc_product){
                    presence = line;
                    return;
                }
            });
            return presence;
        },
        remove_abs_discount: function(){
            var order = this.pos.get_order();
            var abs_disc_product = this.pos.db.get_product_by_id(this.pos.config.discount_abs_product_id[0]);
            var abs_disc_product_price = abs_disc_product.price;
            if (abs_disc_product.taxes_id.length){
                this.pos.taxes_on_discounts = true;
            }
            var lines = order.get_orderlines();
            lines.forEach( function(line){
                if (line.get_product() === abs_disc_product){

                    order.remove_orderline(line);
                }
            });
            return abs_disc_product_price;
        },
        update_summary: function(){
            var order = this.pos.get('selectedOrder');
            this._super();
            if (!this.pos.config.discount_abs_enabled || !order.get_orderlines().length){
                return;
            }
            var total = order
                ? order.get_total_with_tax()
                : 0;
            var abs_prod_id = this.pos.config.discount_abs_product_id[0];
            var abs_disc_prod = this.pos.get_order().get_orderlines().find(function(line){
                return abs_prod_id === line.product.id;
            });
            // taxes_on_discounts is needed to prevent endless cycle caused by negative price due to negative taxes
            if (abs_disc_prod && !this.pos.taxes_on_discounts){
                var recalc = - abs_disc_prod.price !== (Number(this.pos.discount_abs_value) || 0);
                if (( total < 0 || (recalc && total > 0)) ){
                    this.apply_absolute_discount(Math.max(Math.abs(abs_disc_prod.price),this.pos.discount_abs_value || ''))
                }
                total = order
                    ? order.get_total_with_tax()
                    : 0;
            }
            total = total === 0
                ? _t('FREE')
                : Number(total.toFixed(2));
            $('.summary .total > .value').text(total);
        },
    });

    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        set_discount: function(discount){
            if (!this.pos.config.discount_abs_enabled || discount.length >= 2){
                OrderlineSuper.prototype.set_discount.apply(this, [discount]);
                return;
            }
            var previous_disc = this.get_discount() || 0;
            var new_disc = discount === ""
                ? "0"
                : parseFloat(discount) + (previous_disc*10);
            discount = new_disc.toString();
            OrderlineSuper.prototype.set_discount.apply(this, [discount]);
            var products_widgets = this.pos.gui.screen_instances.products;
            if (this.pos.config.discount_abs_enabled && products_widgets &&
                products_widgets.action_buttons && products_widgets.action_buttons.discount){
                this.order.select_orderline(this);
                this.pos.gui.current_screen.numpad.state.set({mode: "discount"});
            }
        },
        get_display_price: function(){
            if (this.pos.config.iface_tax_included) {
                return this.get_price_with_tax() === 0
                    ? _t("FREE")
                    : this.get_price_with_tax();
            }
            return this.get_base_price() === 0
                ? _t("FREE")
                : this.get_base_price();
        },
    });

});
