/* Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */

odoo.define('pos_laundry_management.pos', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var devices = require('point_of_sale.devices');
    var Model = require('web.DataModel');
    var PopupWidget = require('point_of_sale.popups');
    var OrderHistoryScreen = require('pos_orders_history.screens').OrdersHistoryScreenWidget;

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
            return new Model('res.partner').call('load_history', [partner_ids], {'limit': limit}, {'shadow': options.shadow});
        },
        _on_load_history: function(hist){
            var self = this;
            _.each(_.keys(hist), function(pid){
                self.db.get_partner_by_id(pid).history = hist[pid].history;
            });
        },
        lot_barcode_callback: function(res){
            var self = this;
            var popup = this.gui.current_popup
            if (popup && popup.template === "PackLotLinePopupWidget") {
                var el = popup.$el.find('.barcode-input:text');
                el = el.filter(function() { return $(this).val() == ""; }).first();
                el.val(res.code);
            }
        },
    });

    screens.NumpadWidget.include({
        clickAppendNewChar: function(event) {
            var orderline = this.pos.get_order().selected_orderline;
            if (this.state.get('mode') === "quantity" && orderline) {
                var newChar = event.currentTarget.innerText || event.currentTarget.textContent
                var res = undefined;
                if (0 === +this.state.get('buffer') && +newChar <= orderline.quantity) {
                    this.state.set({
                        buffer: orderline.quantity
                    });
                } else {
                    res = this._super.apply(this, arguments);
                }
                if (orderline && orderline.has_product_lot) {
                    this.pos.gui.show_popup('packlotline', {
                        'title': _t('Lot/Serial Number(s) Required'),
                        'pack_lot_lines': orderline.compute_lot_lines(),
                        'order': this.pos.get_order()
                    });
                }
                return res;
            }
            return this._super.apply(this, arguments);
        },

        clickDeleteLastChar: function() {
            var orderline = this.pos.get_order().selected_orderline;
            if (this.state.get('mode') === "quantity" && orderline) {
                if (orderline && orderline.has_product_lot && this.state.get('buffer') !== '') {
                    this.pos.gui.show_popup('packlotline', {
                        'title': _t('Lot/Serial Number(s) Required'),
                        'pack_lot_lines': orderline.compute_lot_lines(),
                        'order': this.pos.get_order()
                    });
                    return undefined;
                }
            }
            return this._super.apply(this, arguments);
        },
        
    });

    gui.Gui.prototype.screen_classes.filter(function(el) {
        return el.name === 'clientlist';
    })[0].widget.include({

        renderElement: function(){
            var self = this;
            this._super();
            var client_button = this.$el.find('#show_clients');
            var history_button = this.$el.find('#show_history');
            var thead_client = this.$el.find('#clientlist_head');
            var thead_history = this.$el.find('#historylist_head');
            var new_client = this.$el.find('.button.new-customer');
            var set_client = this.$el.find('.button.next.highlight');
            client_button.addClass('highlight');
            thead_history.hide();
            this.view_mode = 'show_clients';
            client_button.off().on('click', function(){
                if (!client_button.hasClass('highlight')){
                    history_button.removeClass('highlight');
                    client_button.addClass('highlight');
                    thead_history.hide();
                    thead_client.show();
                    new_client.show();
                    set_client.show();
                    self.view_mode = 'show_clients';
                    self.render_list(self.pos.db.get_partners_sorted(1000));
                }
            });
            history_button.off().on('click', function(){
                if (!history_button.hasClass('highlight')){
                    client_button.removeClass('highlight');
                    history_button.addClass('highlight');
                    thead_client.hide();
                    thead_history.show();
                    new_client.hide();
                    set_client.hide();
                    self.view_mode = 'show_history';
                    self.render_history(self.new_client);
                }
            });
        },
        perform_search: function(query, associate_result) {
            var self = this;
            if (this.view_mode === 'show_history') {
                var res = []
                if (this.new_client) {
                    res = this.new_client.history;
                } else {
                    res = _.flatten(_.map(this.pos.db.get_partners_sorted(1000), function(partner){
                        return partner.history;
                    }));
                }
                res = _.filter(res, function(line){
                   return line.receipt_barcode && line.receipt_barcode.includes(query);
                });
                this.render_history_list(res);
                return;
            }
            this._super(query, associate_result);
        },
        render_history: function(partner) {
            var self = this;
            var history = [];
            var partners = [];
            if (partner){
                this.render_history_list(partner.history);
                partners = [partner]
            } else {
                partners = this.pos.db.get_partners_sorted(1000);
            }
            var partner_ids = _.map(partners, function(partner){
                return partner.id;
            });
            var on_history_load = this.pos.reload_history(partner_ids);
            on_history_load.then(function(){
                history = _.flatten(_.map(partners, function(partner){
                    return partner.history;
                }));
                self.render_history_list(history);
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
            this.$el.find('.receipt_barcode.receipt-button').off().on('click', function(data){
                var partner = self.new_client || self.pos.db.get_partner_by_id(data.currentTarget.getAttribute('p_id'));
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
            var not_int_tags = this.check_tag_correctness(pack_lot_lines.models);
            if (not_int_tags && not_int_tags.length){
                this.show_warns(not_int_tags);
                return;
            }
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
            var numpad_state = this.pos.gui.screen_instances.products.numpad.state;
            numpad_state.set({'buffer': pack_lot_lines.models.length || ''});
            this.options.order.save_to_db();
            this.gui.close_popup();
        },
        check_tag_correctness: function(lots) {
            var el = false;
            var res = [];
            _.each(lots, function(lot){
                el = $('input.tag-input[cid='+ lot.cid +']');
                el.removeClass('warning');
                if (!Number(el.val()) && el.val() !== '') {
                    res.push(lot.cid)
                }
            });
            return res;
        },
        show_warns: function(cids) {
            var el = false;
            _.each(cids, function(c){
                el = $('input.tag-input[cid='+ c +']');
                el.addClass('warning');
            });
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
        show: function(options){
            var self = this;
            this._super(options);
            var line = options.history_line,
                state = line.state;
            if (state && state !== 'cancel') {
                var state_changer = this.$el.find('.button.state_changer');
                var state_cancel = this.$el.find('.button.state_cancel');
                state_changer.off().on('click', function(){
                    var new_state = (state === 'planned' || state === 'confirmed')
                        ? 'cancel'
                        : state === 'progress'
                            ? 'done'
                            : 'progress';
                    self._change_state(line.id, new_state).then(function(data){
                        self._on_changing_status(data[0], line);
                    });
                });
                state_cancel.off().on('click', function(){
                    self._change_state(line.id, 'cancel').then(function(data){
                        self._on_changing_status(data[0], line);
                    });
                });
            }
        },
        _change_state: function(mrp_id, state){
            return new Model('mrp.production').call('set_state', [mrp_id], {'new_state': state});
        },
        _on_changing_status: function(data, line){
            this.pos._on_load_history(data);
            this.gui.current_screen.render_history();
            this.close();
            this.pos.gui.show_popup('receipt_data', {
                'history_line':  _.find(this.pos.db.get_partner_by_id(line.partner_id[0]).history, function(l){
                    return l.id === line.id;
                }),
            });
        },
    });
    gui.define_popup({name:'receipt_data', widget: ReceiptDataPopupWidget});

    devices.BarcodeReader.include({
        init: function (attributes) {
            this._super(attributes);
            this.set_action_callback('lot', _.bind(this.pos.lot_barcode_callback, this.pos));
        },

        scan: function(code){
            if (!code) {
                return;
            }
            var parsed_result = this.barcode_parser.parse_barcode(code);
            var popup = this.pos.gui.current_popup;
            if (parsed_result.type === 'lot' && popup && popup.template === "PackLotLinePopupWidget") {
                if (this.action_callback[parsed_result.type]) {
                    return this.action_callback[parsed_result.type](parsed_result);
                }
                return this.action_callback_stack[0]['lot'](parsed_result)
            }
            return this._super(code);
        },
    });

    OrderHistoryScreen.include({
        show: function () {
            var self = this;
            this._super();
            this.$el.find('tr.order-line .actions .sup_delivery').off().on('click', function (e) {
                var parent = $(this).parents('.order-line');
                var id = parseInt(parent.data('id'));
                self.line_select(e, parent, parseInt(parent.data('id')));
                var sub_delivery_th = parent.next().find('th.sub-delivery');
                var sub_deliveries = parent.next().find('.sub-delivery .state_changer');
                sub_delivery_th.show();
                sub_deliveries.parent('td').show();
                sub_deliveries.on('click', function(e){
                    self._change_order_delivery_states(id, parseInt($(this).parent('td').attr('pid')), 'done');
                });
            });
        },
        _change_order_delivery_states: function(order_id, product_id, state) {
            return new Model('pos.order').call('change_order_delivery_states',
                                               [order_id],
                                               {'product_id': product_id,
                                                'new_state': state,});
        },
    });

});
