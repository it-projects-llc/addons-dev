odoo.define('event_barcode_partner_sale.EventScanViewSale', function (require) {
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

        this.$('div.payment_title').on('click', function(e){
            self.refold_new_attendee_container();
        });

        this.$('div.check_partner_email.btn-primary').on('click', function(e){
            var email_val = self.$('div.attendee_input input.attendee_creation.email_check').val();
            if (email_val) {
                self.make_request_and_update('/event_barcode/check_new_attendee_email', {email: email_val, event_id: self.data.event_id});
            }
        });

        var new_data_container = this.$('#new_attendee_data');
        this.$('div.attendee_input input.attendee_creation.email_check').on('keyup', function(e){
            self.$('div.check_partner_email.received_message').hide();
            self.$('div.check_partner_email.btn-primary').removeClass('disabled');
            new_data_container.hide();
        });

        var attendee_creation_btn = this.$('.create_client.btn.btn-primary');
        var all_att_fields = this.$('.attendee_creation');
        all_att_fields.on('keyup', function(e){
            var vals = _.pluck(all_att_fields, 'value');
            var check = _.find(vals, function(v){
                return !v;
            });
            if (check !== '') {
                attendee_creation_btn.show();
            } else {
                attendee_creation_btn.hide();
            }
        });

        attendee_creation_btn.on('click', function(e){
            var vals = {}
            _.each($('.attendee_creation:not(.event_ticket)'), function(f){
                vals[$(f).getAttributes().name] = f.value;
            });
            self.make_request_and_update('/event_barcode/create_attendee', {
                vals: vals,
                event_id: self.data.event_id,
                event_ticket_id: self.$('.attendee_creation.event_ticket').val(),
                partner_id: new_data_container.getAttributes().pid || 0,
            }).then(function(res){
                console.log(res);
                new_data_container.hide();
                all_att_fields.val('');
                new_data_container.attr('pid', '');
                self.refold_new_attendee_container('fold');
            });
        });

    },

    update_interface_els: function(data) {
        this._super(data);
        if (data.new_attendee) {
            this.update_new_attendee(data.new_attendee);
        }
    },

    update_new_attendee: function(data) {
        var self = this;
        var check_button = this.$('div.check_partner_email.btn-primary');
        var data_container = this.$('#new_attendee_data');
        check_button.addClass('disabled');
        if (data.partner) {
            console.log(data);
            var partner = data.partner;
            var fields = _.keys(partner);
            var input = false;
            _.each(fields, function(f){
                input = data_container.find('input[fdata=' + f + '], select[fdata=' + f + ']');
                input.val(partner[f] || '');
            });
            this.$('#new_attendee_data').attr('pid', partner.id);
        }
        if (!data.existed_attendee) {
            data_container.show();
        }
    },

    refold_new_attendee_container: function(aim){
        var pay_container = this.$('div.payment_container')[0];
        var main_container = this.$('div.o_event_barcode_main')[0];

        if (pay_container.style.display === "block" || aim === 'fold') {
            pay_container.style.display = "none";
            main_container.style.display = "block";
        } else {
            pay_container.style.display = "block";
            main_container.style.display = "none";
        }
    },
});

});
