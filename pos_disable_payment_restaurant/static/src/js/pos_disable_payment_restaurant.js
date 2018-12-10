/* Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
* License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */

odoo.define('pos_disable_payment_restaurant', function(require){

    "use strict";

    var access_right = require('pos_access_right.pos_access_right');
    var screens = access_right.screens;
    var models = access_right.models;
    var core = require('web.core');
    var _t = core._t;

    screens.NumpadWidget.include({
        clickChangeMode: function (event) {
            var res = this._super(event);
            var mode = this.state.get('mode');
            this.check_kitchen_access(mode);
            return res;
        },
        clickDeleteLastChar: function () {
            var order = this.pos.get_order();
            if (this.state.get('mode') === "quantity" &&
                order.get_selected_orderline() &&
                order.get_selected_orderline().quantity <= 0 &&
                order.get_selected_orderline().was_printed &&
                this.pos.get_cashier().groups_id.indexOf(this.pos.config.group_remove_kitchen_order_line_id[0]) === -1) {
                this.gui.show_popup('error', {
                    'title': _t('Cannot kitchen decrease of orderline - Unauthorized function'),
                    'body':  _t('Please ask your manager to do it.'),
                });
            } else if (this.pos.get_cashier().groups_id.indexOf(this.pos.config.group_decrease_kitchen_id[0]) === -1 && (order.get_selected_orderline() && order.get_selected_orderline().was_printed && this.state.get('mode') === 'quantity' )) {
                this.gui.show_popup('error', {
                    'title': _t('Cannot remove kitchen orderline - Unauthorized function'),
                    'body':  _t('Please ask your manager to do it.'),
                });
            } else {
                return this._super();
            }
        },
        check_kitchen_access: function(nodeValue, line) {
            this.disable_numpad = false;
            this.$('.input-button').removeClass('pos-disabled-mode');
            this.$('.numpad-backspace').removeClass('pos-disabled-mode');
            var order = this.pos.get_order();
            if (order) {
                line = line || order.get_selected_orderline();
                var user = this.pos.get('cashier') || this.pos.get_cashier();
                if (user.groups_id.indexOf(this.pos.config.group_decrease_kitchen_id[0]) === -1 && (line && line.was_printed && nodeValue === 'quantity' )) {
                    this.$('.input-button').addClass('pos-disabled-mode');
                    this.$('.numpad-backspace').addClass('pos-disabled-mode');
                    this.disable_numpad = true;
                }
                if (nodeValue === "quantity" && line && line.quantity <= 0 && line.was_printed &&
                    user.groups_id.indexOf(this.pos.config.group_remove_kitchen_order_line_id[0]) === -1) {
                    this.$('.numpad-backspace').addClass('pos-disabled-mode');
                }
            }
        }
    });

    screens.OrderWidget.include({
        start: function () {
            this.pos.bind('change:cashier', this.check_kitchen_access, this);
            this._super();
        },
        orderline_change: function (line) {
            this._super(line);
            var user = this.pos.get('cashier') || this.pos.get_cashier();
            var numpad = this.getParent().numpad;
            this.check_kitchen_access(line);
            if (numpad.disable_numpad || (line && line.quantity <= 0 && user.groups_id.indexOf(this.pos.config.group_delete_order_line_id[0]) === -1 && numpad.state.get('mode') === "quantity") ||
                (line && line.quantity <= 0 && line.was_printed && user.groups_id.indexOf(this.pos.config.group_remove_kitchen_order_line_id[0]) === -1 && numpad.state.get('mode') === "quantity") ||
                (user.groups_id.indexOf(this.pos.config.group_decrease_kitchen_id[0]) === -1 && (line && line.was_printed && numpad.state.get('mode') === 'quantity' ))) {
                $('.numpad-backspace').addClass('pos-disabled-mode');
            } else {
                $('.numpad-backspace').removeClass('pos-disabled-mode');
            }
        },
        renderElement: function (scrollbottom) {
            this._super(scrollbottom);
            this.check_kitchen_access();
        },
        check_kitchen_access: function(line) {
            var numpad = this.getParent().numpad;
            numpad.check_kitchen_access(numpad.state.get('mode'), line);
        }
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        set_dirty: function(dirty) {
            if (this.mp_dirty !== dirty && dirty === false) {
                this.was_printed = true;
            }
            _super_orderline.set_dirty.apply(this,arguments);
        },
        export_as_JSON: function() {
            var data = _super_orderline.export_as_JSON.apply(this, arguments);
            data.was_printed = this.was_printed || [];
            return data;
        },
        init_from_JSON: function(json) {
            this.was_printed = json.was_printed;
            _super_orderline.init_from_JSON.call(this, json);
        }
    });
});
