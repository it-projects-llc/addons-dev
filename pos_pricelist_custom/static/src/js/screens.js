odoo.define('pos_pricelist_custom.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');

    screens.OrderWidget.include({
        orderline_change: function(line){
            this._super(line);
            this.change_selected_line();
        },
        change_selected_line: function() {
            var buttons = this.getParent().action_buttons;
            if (buttons && buttons.pricelist) {
                buttons.pricelist.renderElement();
            }
        },
        change_selected_order: function() {
            this._super();
            var buttons = this.getParent().action_buttons;
            if (buttons && buttons.pricelist) {
                buttons.pricelist.renderElement();
            }
        },
    });

    screens.ClientListScreenWidget.include({
        save_changes: function () {
            this._super();
            if (this.has_client_changed()) {
                var buttons = this.getParent().screens.products.action_buttons;
                if (buttons && buttons.pricelist) {
                    buttons.pricelist.renderElement();
                }
            }
        }
    });

    screens.PricelistButton = screens.ActionButtonWidget.extend({
        template: 'PricelistButton',
        button_click: function() {
            var order = this.pos.get_order();
            var orderline = order.get_selected_orderline();
            if (orderline) {
                this.apply_pricelist(orderline);
            }
        },
        apply_pricelist: function(line) {
            var pricelist = this.pos.default_pricelist;
            if (line.pricelist && line.pricelist.id !== pricelist.id) {
                line.set_default_pricelist();
            }
        },
        get_pricelist_name: function(){
            var pricelist = this.pos.default_pricelist;
            var current_order = this.pos.get_order();
            if (current_order) {
                var partner = current_order.get_client() || false;
                var line = current_order.get_selected_orderline();
                if (line && line.pricelist.id !== pricelist.id && current_order.pricelist) {
                    pricelist = current_order.pricelist;
                }
            }
            return pricelist.name;
        },
        renderElement: function(){
            this._super();
            var pricelist = this.pos.default_pricelist;
            var current_order = this.pos.get_order();
            if (current_order) {
                var line = current_order.get_selected_orderline();
                if (line && line.pricelist.id && line.pricelist.id !== pricelist.id) {
                    this.highlight(true);
                } else {
                    if (line && !line.pricelist.id && current_order.pricelist.id !== pricelist.id) {
                        this.highlight(true);
                    } else {
                        this.highlight(false);
                    }
                }
            }
        }
    });

    screens.define_action_button({
        'name': 'pricelist',
        'widget': screens.PricelistButton,
        'condition': function(){
            return this.pos.config.show_orderline_default_pricelist;
        },
    });

    return screens;
});
