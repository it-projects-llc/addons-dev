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

        var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        reload_history: function(partner_ids, limit, options){
            /**
             @param {Array} partner
             @param {Number} limit
             @param {Object} options
               * "shadow" - set true to load in background (i.e. without blocking the screen). Default is True
             **/
            var self = this;
            limit = limit || 0;
            options = options || {};

            if (typeof options.shadow === "undefined"){
                options.shadow = true;
            }

            var def = $.when();

            return def.then(function(){
                var request_finished = $.Deferred();

                self._load_history(partner_ids, limit, options).then(function (data) {
                    self._on_load_history(data);
                }).always(function(){
                    request_finished.resolve();
                }).fail(function () {
                    self.reload_history(partner_ids, 0, {"postpone": 4000, "shadow": false});
                });
                return request_finished;
            });

        },
        _load_history: function(partner_ids, limit, options){
            return new Model('mrp.production').call('load_history', [partner_ids], {'limit': limit}, {'shadow': options.shadow});
        },
        _on_load_history: function(hist){
            var self = this;
            _.each(_.keys(hist), function(pid){
                self.db.get_partner_by_id(pid).history = hist[pid].history;
            });
        },
    });

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
                    self.render_history(self.new_client);
                }
            });
            console.log('dfsdfsdf')
        },

        render_history: function(partner) {
            var self = this;
            partner = partner || self.new_client || self.old_client;
            this.render_history_list(partner.history);
            var history = this.pos.reload_history(partner.id);
            history.then(function(){
                self.render_history_list(partner.history);
            });
        },
        render_history_list: function(history_lines) {
            var contents = this.$el[0].querySelector('.client-list-contents');
            contents.innerHTML = "";
            if (history_lines && history_lines.length) {
                for (var y = 0; y < history_lines.length; y++) {
                    var history_line_html = QWeb.render('HistoryLine', {
                        line: history_lines[y],
                        widget: self,
                    });
                    var history_line = document.createElement('tbody');
                    history_line.innerHTML = history_line_html;
                    history_line = history_line.childNodes[1];
                    contents.appendChild(history_line);
                }
            }
        },

    });

});
