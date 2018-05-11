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


    models.load_fields('res.partner','phonetic_name');

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
        
    });

    gui.Gui.prototype.screen_classes.filter(function(el) {
        return el.name === 'clientlist';
    })[0].widget.include({

        display_client_details: function(visibility,partner,clickpos){
            var self = this;
            this._super(visibility,partner,clickpos);

            var client_button = this.$el.find('#show_clients');
            var history_button = this.$el.find('#show_history');
            var thead_client = this.$el.find('#clientlist_head');
            var thead_history = this.$el.find('#historylist_head');
            client_button.addClass('highlight');
            thead_history.hide();
            client_button.off().on('click', function(){
                if (!client_button.hasClass('highlight')){
                    history_button.removeClass('highlight');
                    client_button.addClass('highlight');
                    thead_history.hide();
                    thead_client.show();
                    self.render_list(self.pos.db.get_partners_sorted(1000))
                }
            });
            history_button.off().on('click', function(){
                if (!history_button.hasClass('highlight')){
                    client_button.removeClass('highlight');
                    history_button.addClass('highlight');
                    thead_client.hide();
                    thead_history.show();
                    self.render_history(self.pos.db.get_partner_by_id(8));
                }
            });
            console.log('dfsdfsdf')
        },

        render_history: function(partner) {
            var self = this;
            var contents = this.$el[0].querySelector('.client-list-contents');
            contents.innerHTML = "";
            var lines = [
                {
                    'receipt_id': 1,
                    'date': 2,
                    'status': 3,
                    'fin_date': 4,
                },
                {
                    'receipt_id': 1,
                    'date': 2,
                    'status': 3,
                    'fin_date': 4,
                }
            ]
            for (var y = 0; y < lines.length; y++) {
                var history_line_html = QWeb.render('HistoryLine', {
                    line: lines[y],
                    widget: self,
                });
                var history_line = document.createElement('tbody');
                history_line.innerHTML = history_line_html;
                history_line = history_line.childNodes[1];
                contents.appendChild(history_line);
            }
        },

    });

});
