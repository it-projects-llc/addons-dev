odoo.define('event_barcode_partner.EventScanView', function (require) {
"use strict";

var bus = require('bus.bus');
var Session = require('web.session');
var local_storage = require('web.local_storage');
var event_barcode = require('event_barcode.EventScanView');

var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;


event_barcode.EventScanView.include({

    start: function() {
        var self = this;
        this._super.apply(this, arguments);

        function isLetter(str) {
          return str.length === 1 && str.match(/[a-z]/i);
        }

//        this.$('input#event_client_name_search').on('change', function(e){
//            var name = e.target.value;
//            self.on_name_entered(name);
//        });
        this.$('input#event_client_name_search').on('keypress', function(e){
            var name = isLetter(e.key)
             ? e.target.value + e.key
             : e.target.value;
            if (name) {
                self.on_name_entered(name);
            }
        });

        this.update_session_id().then(function(data){
            self.update_bus();
        });

    },

    update_bus: function(){
        var self = this;
        this.bus = bus.bus;
        this.bus.stop_polling();
        var channel_name = this.get_full_channel_name('bi.longpolling.notifs', this.interface_session_number + '')
        this.bus.add_channel(channel_name);
        this.force_start_polling();
        this.bus.on("notification", this.bus, function(data){
            if (data && data.length){
                self.update_client_list(JSON.parse(data[0][1]));
            }
        });
    },

    force_start_polling: function(){
        this.bus.start_polling();
        if(!this.bus.activated){
            this.bus.poll();
            this.bus.stop = false;
        }
    },

    get_full_channel_name: function(channel_name, sub_channel){
        return JSON.stringify([Session.db,channel_name,sub_channel]);
    },

    on_barcode_scanned: function(barcode) {
        var self = this;
        if (this.attendee && barcode.startsWith('05')) {
            this.make_request_and_update('/event_barcode/set_rfid', {
                 aid: this.attendee.aid,
                 rfid: barcode,
            });
        } else {
            this._super.apply(this, arguments);
        }
        this.make_request_and_update('/event_barcode/get_attendee_by_barcode', {
             barcode: barcode,
             event_id: this.action.context.active_id
        });
    },

    on_manual_scan: function(e) {
        if (e.which === 13) { // Enter
            var barcode = $(e.currentTarget).val().trim();
            if (this.attendee && barcode.startsWith('05')) {
                this.make_request_and_update('/event_barcode/set_rfid', {
                     aid: this.attendee.aid,
                     rfid: barcode,
                });
            } else {
                this._super.apply(this, arguments);
            }
        }
    },

    on_barcode_scanned_explicit: function(barcode) {
        this._super.apply(this, arguments).then(function(result){
            if (result.success) {
                self.updateCount(
                    self.$('.o_event_reg_attendee'),
                    result.count
                );
                // HERE IS NECESSARY TO UPDATE SERVER RESPONSE
                self.set_attendee_by_id();
                self.notification_manager.success(result.success);
            } else if (result.warning) {
                self.do_warn(_("Warning"), result.warning);
            }
        });
    },

    on_name_entered: function(name) {
        this.make_request_and_update('/event_barcode/get_attendees_by_name', {
             name: name,
             event_id: this.action.context.active_id
        });
    },

    update_client_list: function(data) {
        var self = this;
        var row_html = '';
        var table = this.$('.o_event_barcode_detail.client_info.text-center');
        var old_rows = table.find('.client_cell');

        this.attendees = data;
        this.set_attendee_by_id();

        old_rows.remove();
        _.each(data, function(att){
            row_html = QWeb.render('client_row', {'att':att}) ;
            table.append(row_html);
        });
        var new_rows = table.find('.client_cell').on('click', function(e){
            var row = e.target.closest('.client_cell');
            var list = row.parentElement;

            var aid = row.getAttribute('aid');
            $(list).find('.rfid').hide();
            $(row).find('.rfid').show();
            $(row).find('.sign_request').off().on('click', function(e){
                Session.rpc('/event_barcode/sign_request', {
                     attendee_id: aid,
                     event_id: self.action.context.active_id,
                     barcode_interface_id: self.interface_session_number,
                     //db_name: Session.db
                });
            });
            $(row).find('.accept_request').off().on('click', function(e){
                Session.rpc('/event_barcode/register_attendee_by_id', {
                     attendee_id: aid,
                }).then(function(result) {
                    if (result.success) {
                        self.updateCount(
                            self.$('.o_event_reg_attendee'),
                            result.count
                        );
                        self.notification_manager.success(result.success);
                    } else if (result.warning) {
                        self.do_warn(_("Warning"), result.warning);
                    }
                    self.update_client_list(result.attendee);
                });
            });
            self.set_attendee_by_id(aid);
        });

        if (data.length === 1) {
            this.$('.o_event_barcode_detail.client_info.text-center .client_cell').find('.rfid').show();
            this.set_attendee_by_id(data[0].aid);
        }
    },

    set_attendee_by_id: function(aid) {
        aid = parseInt(aid);
        this.attendee = _.find(this.attendees, function(a){
            return a.aid === aid;
        });
    },

    make_request_and_update: function(rout, vals) {
        var self = this;
        return Session.rpc(rout, vals).then(function(result) {
            self.update_client_list(result);
        });
    },

    update_session_id: function() {
        var self = this;
        var def = $.Deferred();
        this.interface_session_number = this.get_from_storage('interface_session_number');
        if (this.interface_session_number) {
            this.save_locally('interface_session_number', this.interface_session_number);
            this.render_session_id();
            def.resolve();
        } else {
            this.get_new_session_id().always(function(){
                def.resolve();
            });
        }
        return def;
    },

    get_new_session_id: function() {
        var self = this;
        return Session.rpc('/event_barcode/new_session', {
            event_id: self.action.context.active_id
        }).then(function(result) {
            result = parseInt(result);
            self.interface_session_number = result;
            self.save_locally('interface_session_number', self.interface_session_number);
            self.render_session_id();
        });
    },

    render_session_id: function(){
        var row_html = QWeb.render('session_number_h1', {'session_number':this.interface_session_number}) ;
        this.$el.find('.o_event_barcode_main').prepend(row_html);
    },

    save_locally: function(key, value) {
        local_storage.setItem('est.' + key, JSON.stringify(value));
    },

    get_from_storage: function(key) {
        return JSON.parse(local_storage.getItem('est.' + key));
    },

});

});
