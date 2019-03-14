/*  Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_esign_request.esign_request', function (require) {
"use strict";

//var bus = require('bus.bus');
//var local_storage = require('web.local_storage');

var Session = require('web.session');
var screens = require('point_of_sale.screens');
var models = require('point_of_sale.models');
var gui = require('point_of_sale.gui');
var core = require('web.core');

var QWeb = core.qweb;
var _t = core._t;

models.load_fields("res.partner", ['sign_attachment_id']);

screens.PaymentScreenWidget.include({

    show: function(parent, options) {
        var self = this;
        this._super(parent, options);

        var esign_button = this.$el.find('.button.esign');
        esign_button.hide();
        var next_button = $('.payment-screen .top-content .button.next').hide();

        var client = this.pos.get_client();
        var ask_for_sign = this.pos.config.ask_for_sign;
        if (ask_for_sign && client) {
            esign_button.show();
            esign_button.off().on('click', function(e){
                var partner = self.pos.get_client();
                if (!partner){
                    return self.click_set_customer();
                }
                self.pos.esign_request(self.compose_vals_for_sign_request());
            });
            var mandatory_ask_for_sign = this.pos.config.mandatory_ask_for_sign;
            if (!mandatory_ask_for_sign || client.sign_attachment_id) {
                next_button.show();
            }
        } else if (!ask_for_sign) {
            next_button.show();
        }


        this.pos.bind('changed:partner_esign', function(res){
            var client = self.pos.get_client();
            if (client && client.id === res.partner_id && client.sign_attachment_id) {
                next_button.show();
            }
        });
    },

    compose_vals_for_sign_request: function(){
        var partner = self.pos.get_client();
        return {
            partner_id: partner.id,
            partner_name: partner.name,
            config_id: this.pos.config.id,
        };
    }

});

gui.Gui.prototype.screen_classes.filter(function(el) {
    return el.name === 'clientlist';
})[0].widget.include({

    show: function(){
        this._super();
        var self = this;

        var esign_button = this.$el.find('.button.esign');
        if (!this.pos.config.ask_for_sign) {
            esign_button.hide();
        } else {
            esign_button.off().on('click', function(e){
                var partner = self.new_client || self.old_client;
                if (!partner) {
                    return;
                }
                Session.rpc('/pos_longpolling/sign_request', {
                    vals: {
                        partner_id: partner.id,
                        partner_name: partner.name,
                        config_id: self.pos.config.id,
                    },
                });
            });
        }

        this.pos.bind('changed:partner_esign', function(res){
            var partners = self.pos.db.get_partners_sorted(1000);
            self.$el.find('tr[data-id="' + res.partner_id + '"] td.esign').text("✔");
        });
    },

});

var PosModelSuper = models.PosModel;
models.PosModel = models.PosModel.extend({
    initialize: function(){
        var self = this;
        PosModelSuper.prototype.initialize.apply(this, arguments);

        this.ready.then(function () {
            if (!self.config.ask_for_sign) {
                return;
            }
            var channel_name = "pos.sign_request";
            var callback = self.updates_from_sign_kiosk;
            var bus = self.get_bus();
            bus.add_channel_callback(channel_name, self.esign_callback, self);
            bus.start();
        });
    },

    esign_callback: function(res){
        if (!res) {
            return;
        }
        res = JSON.parse(res);

        var partner = this.db.get_partner_by_id(res.partner_id);
        if (partner) {
            partner.sign_attachment_id = res.attachment_id;
            this.trigger('changed:partner_esign', res);
        }
    },

    esign_request: function(vals) {
        Session.rpc('/pos_longpolling/sign_request', {
            vals: vals,
        });
    },

});

});
