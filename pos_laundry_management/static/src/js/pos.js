/* Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */

odoo.define('pos_laundry_management.pos', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var utils = require('web.utils');
    var Model = require('web.DataModel');
    var PopupWidget = require('point_of_sale.popups');

    var QWeb = core.qweb;
    var _t = core._t;


    screens.NumpadWidget.include({
        clickAppendNewChar: function(event) {
            if (this.pos.get_order().selected_orderline.has_product_lot) {
                var pack_lot_lines_length =  this.pos.get_order().selected_orderline.compute_lot_lines().length;
                var newChar = 0;
                newChar = Math.max(event.currentTarget.innerText || event.currentTarget.textContent,
                                   pack_lot_lines_length);
                var res = this.state.appendNewChar(newChar);
                this.pos.gui.show_popup('packlotline', {
                    'title': _t('Lot/Serial Number(s) Required'),
                    'pack_lot_lines': this.pos.get_order().selected_orderline.compute_lot_lines(),
                    'order': this.pos.get_order()
                });
                return res;
            }
            return this._super.apply(this, arguments);
        },

        clickDeleteLastChar: function() {
            var res = this._super.apply(this, arguments);
            if (this.pos.get_order().selected_orderline.has_product_lot) {
                this.pos.gui.show_popup('packlotline', {
                    'title': _t('Lot/Serial Number(s) Required'),
                    'pack_lot_lines': this.pos.get_order().selected_orderline.compute_lot_lines(),
                    'order': this.pos.get_order()
                });
                return undefined;
            }
            return this._super.apply(this, arguments);
        },

    })

});
