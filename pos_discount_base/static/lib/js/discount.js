odoo.define('pos_discount_base.screens', function (require) {
    "use strict";

    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');

    PosBaseWidget.include({
        init:function(parent,options){
            var self = this;
            this._super(parent,options);
            if (this.gui && this.gui.screen_instances.products && this.gui.screen_instances.products.action_buttons.discount) {
                var disc_widget = this.gui.screen_instances.products.action_buttons.discount;
                disc_widget.apply_discount = function(pc) {
                    self.gui.screen_instances.products.order_widget.apply_discount(pc);
                };
                disc_widget.button_click = function () {
                    self.gui.screen_instances.products.order_widget.discount_options = {
                        'title': 'Discount Percentage',
                        'value': this.pos.config.discount_pc,
                    };
                    self.gui.screen_instances.products.order_widget.discount_button_click();
                };
            }
        },
    });

    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        export_as_JSON: function() {
            var ret = OrderlineSuper.prototype.export_as_JSON.apply(this);
            ret.price_manually_set = this.price_manually_set;
            return ret
        },
        init_from_JSON: function(json) {
            OrderlineSuper.prototype.init_from_JSON.apply(this,arguments);
            this.price_manually_set = json.price_manually_set;
        },
    });

    screens.OrderWidget.include({
        // COPY FROM pos_discount/static/src/js/discount.js
        apply_discount: function(pc) {
            var order    = this.pos.get_order();
            var lines    = order.get_orderlines();
            var product  = this.pos.db.get_product_by_id(this.pos.config.discount_product_id[0]);

            // Remove existing discounts
            var i = 0;
            while ( i < lines.length ) {
                if (lines[i].get_product() === product) {
                    order.remove_orderline(lines[i]);
                } else {
                    i++;
                }
            }
            // Add discount
            var discount = - pc / 100.0 * order.get_total_with_tax();

            if( discount < 0 ){
                order.add_product(product, { price: discount });
            }

            // prevents setting discount to a default value when partner changing (set_pricelist)
            this.pos.get_order().get_selected_orderline().price_manually_set = true;
        },
        // DIFFERENCES FROM ORIGINAL:
        // confirm is separate function
        discount_button_click: function() {
            var self = this;
            this.discount_options.confirm = function(val) {
                self.confirm_discount(val);
            };
            this.gui.show_popup('number', this.discount_options);
        },
        confirm_discount: function(val) {
            val = Math.round(Math.max(0,Math.min(100,val)));
            this.apply_discount(val);
        },
    });
    return screens;
});
