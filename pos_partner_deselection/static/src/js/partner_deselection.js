odoo.define('pos_partner_deselection.partner_deselection', function (require) {
"use strict";

var bus = require('bus.bus');
var Session = require('web.session');
var local_storage = require('web.local_storage');
var event_barcode = require('event_barcode.EventScanView');

var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;


var models = require('point_of_sale.models');

var _super_posmodel = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({

    initialize: function (session, attributes) {
        var self = this;
        _super_posmodel.initialize.apply(this, arguments);

        this.ready.then(function () {
            if (self.config.customer_deselection_interval) {
                _.each(self.get_order_list(), function(ord){
                    ord.set_client();
                });
            }
        });
    },

});

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({

    set_client: function(client) {
        var self = this;
        _super_order.set_client.apply(this, arguments);
        var customer_deselection_interval = this.pos.config.customer_deselection_interval;
        if (customer_deselection_interval && client && !self.finalized) {
            setTimeout(function() {
                self.set_client();
            }, customer_deselection_interval * 1000);
        }
    },

});

});
