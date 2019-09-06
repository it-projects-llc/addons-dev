/* Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73>
* License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_cashbox_pins.open', function (require) {
    "use strict";

    var Session = require('web.Session');
    var core = require('web.core');
    var CrashManager = require('web.CrashManager');
    var screens = require('point_of_sale.screens');
    var rpc = require('web.rpc');

    var _t = core._t;

    screens.PaymentScreenWidget.include({

        init: function(parent, options) {
            this._super(parent,options);
            options = options || {};
            var url = this.gui.pos.config.proxy_ip;
            var protocol = window.location.protocol;
            if (url){
                var port = ':8069';
                if (protocol === "https:") {
                    port = ':443';
                }
                if(url.indexOf('//') < 0){
                    url = protocol + '//' + url;
                }
                if(url.indexOf(':',5) < 0){
                    url += port;
                }
                this.connection = new Session(void 0,url, { use_cors: true});
            }
        },

        renderElement: function(){
            var self = this;
            this._super();
            this.$('.js_cashdrawer_pin').click(function(){
                self.pin_request();
            });
        },

        pin_request: function(){
            var self = this;
            var cashier = this.pos.get_cashier();
            return this.gui.ask_password(cashier.pos_security_pin).then(function(result){
                if (self.connection){
                    return self.connection.rpc('/pos_cashbox_pin/open_cashbox',{},{timeout:2500}).then(function(result){
                        console.log(result)
                    };
                };
            });
        },
    });
});
