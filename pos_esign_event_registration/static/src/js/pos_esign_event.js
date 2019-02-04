/*  Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_esign_event_registration.pos_event', function (require) {
"use strict";

//var screens = require('point_of_sale.screens');
//var devices = require('point_of_sale.devices');
//var gui = require('point_of_sale.gui');
//var PosDB = require('point_of_sale.DB');
//var Model = require('web.DataModel');

var Session = require('web.session');
var models = require('point_of_sale.models');
var pos_event = require('pos_event_registration.pos_event');

var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;


models.load_fields('event.event',['mandatory_esign', 'terms_to_sign']);
models.load_fields('event.registration',['signed_terms', 'completed_document']);


var PosModelSuper = models.PosModel;
models.PosModel = models.PosModel.extend({
    esign_callback: function(res){
        PosModelSuper.prototype.esign_callback.apply(this, arguments);
        var res = JSON.parse(res);
        if (res.attendee_id){
            this.trigger('changed:attendee_esign', res);
        }
    },

});

pos_event.AttendeeListScreenWidget.include({
    show: function(parent, options) {
        var self = this;
        this._super(parent, options);

        var esign_button = this.$el.find('.button.esign').hide();

        esign_button.off().on('click', function(e){
            var attendee = self.current_attendee;
            if (attendee){
                Session.rpc('/pos_longpolling/sign_request', {
                    vals: {
                        partner_id: attendee.partner_id[0],
                        partner_name: attendee.partner_id[1],
                        config_id: self.pos.config.id,
                        attendee_id: attendee.id,
                    },
                });
            }
        });

        this.pos.bind('changed:attendee_esign', function(res){
            if (res.attendee_id && self.current_attendee && res.attendee_id === self.current_attendee.id &&
                res.signed_terms) {
                self.$el.find('.button.attendeed').show();
                self.reload_attendees();
            }
        });
    },

    validate_attendee: function() {
        var self = this;
        // take attendee from db to process fully updated attendee
        var attendee = this.pos.db.get_attendee_by_id(this.current_attendee.id);
        if (this.pos.config.ask_attendees_for_esign && attendee && !attendee.signed_terms) {
            self.gui.show_popup('error',{
                'title': _t('Error: Could not Accept Attendee'),
                'body': 'Terms are not signed',
            });
            return false;
        }
        return this._super();
    },

    line_select: function(event, $line, id){
        this._super(event, $line, id);
        var esign_button = this.$el.find('.button.esign');
        var attendeed_button = this.$el.find('.button.attendeed');

        if ( $line.hasClass('highlight') ){
            attendeed_button.hide();
            esign_button.show();
            this.action_show_attendeed_button();
        } else {
            esign_button.hide();
            attendeed_button.hide();
        }
    },
    action_show_attendeed_button: function(){
        var $button_attendee = this.$('.button.attendeed.highlight');
        if(this.current_attendee && this.current_attendee.signed_terms){
            this._super();
        } else {
            $button_attendee.hide();
        }
    },
});

});
