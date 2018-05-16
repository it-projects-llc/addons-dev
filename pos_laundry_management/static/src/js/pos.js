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
            var orderline = this.pos.get_order().selected_orderline;
            if (orderline && orderline.has_product_lot) {
                var pack_lot_lines_length =  orderline.compute_lot_lines().length;
                var newChar = 0;
                newChar = Math.max(event.currentTarget.innerText || event.currentTarget.textContent,
                                   pack_lot_lines_length);
                var res = this.state.appendNewChar(newChar);
                this.pos.gui.show_popup('packlotline', {
                    'title': _t('Lot/Serial Number(s) Required'),
                    'pack_lot_lines': orderline.compute_lot_lines(),
                    'order': this.pos.get_order()
                });
                return res;
            }
            return this._super.apply(this, arguments);
        },

        clickDeleteLastChar: function() {
            var res = this._super.apply(this, arguments);
            var orderline = this.pos.get_order().selected_orderline;
            if (orderline && orderline.has_product_lot) {
                this.pos.gui.show_popup('packlotline', {
                    'title': _t('Lot/Serial Number(s) Required'),
                    'pack_lot_lines': orderline.compute_lot_lines(),
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
            var self = this;
            var contents = this.$el[0].querySelector('.client-list-contents');
            contents.innerHTML = "";
            if (history_lines && history_lines.length) {
                for (var y = history_lines.length - 1; y >= 0; y--) {
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
            this.$el.find('.receipt_barcode').off().on('click', function(data){
                var partner = self.new_client || self.old_client;
                var hl_id = data.currentTarget.getAttribute('hl_id');
                var history_line = _.find(partner.history, function(hl){
                    return hl.id == hl_id;
                });
                self.pos.gui.show_popup('receipt_data', {
                    'history_line':  history_line,
                });
            });
        },

    });

    gui.Gui.prototype.popup_classes.filter(function(el) {
        return el.name === 'packlotline';
    })[0].widget.include({
        click_confirm: function(){
            var pack_lot_lines = this.options.pack_lot_lines;
            this.$('.table-row').each(function(index, el){
                var cid = $(el).find('.barcode-input').attr('cid'),
                    lot_name = $(el).find('.barcode-input').val(),
                    tag = $(el).find('.tag-input').val();
                var pack_line = pack_lot_lines.get({cid: cid});
                pack_line.set_lot_name(lot_name);
                pack_line.set_tag(tag);
            });
            pack_lot_lines.remove_empty_model();
            pack_lot_lines.set_quantity_by_lot();
            this.options.order.save_to_db();
            this.gui.close_popup();
        },
    });

    var PacklotlineSuper = models.Packlotline;
    models.Packlotline = models.Packlotline.extend({
        export_as_JSON: function() {
            var res = PacklotlineSuper.prototype.export_as_JSON.apply(this, arguments);
            res.tag = this.get_tag();
            return res;
        },
        set_tag: function(name){
            this.set({tag : _.str.trim(name) || null});
        },
        get_tag: function(){
            return this.get('tag');
        },
        init_from_JSON: function(json) {
            this.order_line = json.order_line;
            this.set_lot_name(json.lot_name);
            this.set_tag(json.tag);
        },
    });

    var ReceiptDataPopupWidget = PopupWidget.extend({
        template: 'ReceiptDataPopupWidget',
    });
    gui.define_popup({name:'receipt_data', widget: ReceiptDataPopupWidget});

});
