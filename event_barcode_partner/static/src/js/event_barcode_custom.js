odoo.define('event_barcode_partner.EventScanView', function (require) {
"use strict";

var bus = require('bus.bus');
var Session = require('web.session');
var local_storage = require('web.local_storage');
var event_barcode = require('event_barcode.EventScanView');
var Notification = require('web.notification').Notification;
var NotificationManager = require('web.notification').NotificationManager;

var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;

// Success Notification with thumbs-up icon
var Error = Notification.extend({
    template: 'event_barcode_error'
});

var Warning = Notification.extend({
    template: 'event_barcode_warning'
});

event_barcode.NotificationSuccess.include({
    error: function(title, text, sticky) {
        return this.display(new Error(this, title, text, sticky));
    },
    warning: function(title, text, sticky) {
        return this.display(new Warning(this, title, text, sticky));
    }
});

event_barcode.EventScanView.include({

    start: function() {
        var self = this;
        this._super.apply(this, arguments);

        function isLetter(str) {
          return str.length === 1 && str.match(/[a-z]/i);
        }

        this.$('input#event_client_name_search').on('keyup', function(e){
            self.on_name_entered(e.target.value);
        });

        this.$('div.bracelets_title').on('click', function(e){
            var container = self.$('div.bracelet_container')[0];
            if (container.style.display === "none") {
                container.style.display = "block";
            } else {
                container.style.display = "none";
            }
        });

        this.update_session_id().then(function(data){
            self.update_bus();
        });

        this.rfid_templates = this.data.rfid_templates && this.data.rfid_templates.split(',');
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
                self.update_interface_els(JSON.parse(data[0][1]));
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

    check_barcode_template: function(barcode) {
        var self = this;
        return _.find(this.rfid_templates, function(t){
            return barcode.startsWith(t);
        });
    },

    on_barcode_scanned: function(barcode) {
        var self = this;
        if (this.attendee && this.check_barcode_template(barcode)) {
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
            if (this.attendee && this.check_barcode_template(barcode)) {
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
        if (name) {
            this.make_request_and_update('/event_barcode/get_attendees_by_name', {
                 name: name,
                 event_id: this.action.context.active_id
            });
        } else {
            this.update_client_list(false);
        }
    },

    update_interface_els: function(data) {
        if (data.attendees) {
            this.update_client_list(data.attendees);
        }
        if (data.bracelets) {
            this.update_bracelet_table(data.bracelets);
        }
        if (data.notification) {
            this.show_message(data.notification);
        }
    },

    show_message: function(data) {
        if (data.type === 'warning') {
            data.sticky = data.sticky || 5000;
        }
        if (this.notification_manager[data.type]) {
            this.notification_manager[data.type](data.header, data.text);
        }
    },

    update_client_list: function(data) {
        var self = this;
        var row_html = '';
        var table = this.$('.o_event_barcode_detail.client_info.text-center');
        var old_rows = table.find('.client_cell');

        var openInNewTab = function(url) {
          var win = window.open(url, '_blank');
          win.focus();
        }

        this.attendees = data;
        this.set_attendee_by_id();

        old_rows.remove();
        _.each(data, function(att){
            row_html = QWeb.render('client_row', {'att':att}) ;
            table.append(row_html);
        });
        var new_rows = table.find('.client_cell').on('click', function(e){
            var row = e.target.closest('.client_cell');
            self.open_and_activate_row_actions(row);
        });

        if (data.length === 1) {
            var client_row = this.$('.o_event_barcode_detail.client_info.text-center .client_cell');
            self.open_and_activate_row_actions(client_row[0]);
            this.set_attendee_by_id(data[0].aid);
        }
    },

    open_and_activate_row_actions: function(row){
        var self = this;

        var list = row.parentElement;
        var aid = row.getAttribute('aid');
        $(list).find('.rfid').hide();
        $(row).find('.rfid').show();
        $(row).find('.o_client_div').off().on('click', function(e){
            var url = self.data.attendee_url[0] + aid + self.data.attendee_url[1];
            openInNewTab(url);
        });

        var show_custom_rfid_setting = function(row){
            $(row).find('.set_rfid_input').show().find('input').focus();
            $(row).find('.set_rfid').show();
            $(row).find('.discard_rfid').show();
            $(row).find('.change_rfid').hide();
            $(row).find('.add_rfid').hide();
        };

        var hide_custom_rfid_setting = function(row){
            $(row).find('.set_rfid_input').hide().find('input').focusout();
            $(row).find('.set_rfid').hide();
            $(row).find('.discard_rfid').hide();
            if (self.attendee.rfid) {
                $(row).find('.change_rfid').show();
            } else {
                $(row).find('.add_rfid').show();
            }
        };

        $(row).find('.rfid_button.add_rfid').off().on('click', function(e){
            show_custom_rfid_setting(row);
        });
        $(row).find('.rfid_button.change_rfid').off().on('click', function(e){
            show_custom_rfid_setting(row);
        });
        $(row).find('.rfid_button.discard_rfid').off().on('click', function(e){
            hide_custom_rfid_setting(row);
        });
        $(row).find('.rfid_button.set_rfid').off().on('click', function(e){

            var input_value = $(row).find('.set_rfid_input input').val();
            if (input_value) {
                self.make_request_and_update('/event_barcode/set_rfid', {
                     aid: self.attendee.aid,
                     rfid: input_value,
                }).then(function(res){
                    hide_custom_rfid_setting(row);
                });
            }

        });

        $(row).find('.sign_request').off().on('click', function(e){
            Session.rpc('/event_barcode/sign_request', {
                 attendee_id: aid,
                 event_id: self.action.context.active_id,
                 barcode_interface_id: self.interface_session_number,
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
                self.update_interface_els(result.data);
            });
        });
        this.set_attendee_by_id(aid);
    },

    update_bracelet_table: function(data) {
        var self = this;
        var bracelet_container = this.$('.bracelet_container');
        bracelet_container[0].innerHTML = '';
        var new_table = QWeb.render('bracelet_table', {'bracelets':data}) ;
        bracelet_container.append(new_table);
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
            self.update_interface_els(result);
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
