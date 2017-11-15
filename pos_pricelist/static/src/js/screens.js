/******************************************************************************
*    Point Of Sale - Pricelist for POS Odoo
*    Copyright (C) 2014 Taktik (http://www.taktik.be)
*    @author Adil Houmadi <ah@taktik.be>
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Affero General Public License as
*    published by the Free Software Foundation, either version 3 of the
*    License, or (at your option) any later version.
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Affero General Public License for more details.
*    You should have received a copy of the GNU Affero General Public License
*    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
******************************************************************************/
odoo.define('pos_pricelist.screens', function (require) {
	"use strict";

	var screens = require('point_of_sale.screens');
	var core = require('web.core');

    screens.ClientListScreenWidget.include({
        save_changes: function () {
            this._super();
            if (this.has_client_changed()) {
                var currentOrder = this.pos.get('selectedOrder');
                var orderLines = currentOrder.orderlines.models;
                var partner = currentOrder.get_client();
                this.pos.pricelist_engine.update_products_ui(partner);
                this.pos.pricelist_engine.update_ticket(partner, orderLines);
                if (partner && partner.property_product_pricelist[0] !== this.pos.config.pricelist_id[0]) {
                    var buttons = this.getParent().screens.products.action_buttons;
                    if (buttons && buttons.pricelist) {
                        if (orderLines.length) {
                            orderLines.forEach(function(line){
                                buttons.pricelist.set_change_pricelist_button(true, line)
                            });
                        }
                    }
                }
            }
        }
    });
    var PricelistButton = screens.ActionButtonWidget.extend({
        template: 'PricelistButton',
        button_click: function() {
            var order = this.pos.get_order();
            var orderline = order.get_selected_orderline();
            if (orderline.default_pricelist_is_active) {
                this.apply_pricelist();
            }
        },
        apply_pricelist: function() {
            var order = this.pos.get_order();
            var line = order.get_selected_orderline();
            this.set_change_pricelist_button(false, line);
        },
        set_change_pricelist_button(status, line) {
            this.highlight(status);
            if (line) {
                line.default_pricelist_is_active = status;
            }
        },
    });

    screens.define_action_button({
        'name': 'pricelist',
        'widget': PricelistButton,
    });
});
