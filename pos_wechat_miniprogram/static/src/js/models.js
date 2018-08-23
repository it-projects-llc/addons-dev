/* Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
   License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_wechat_miniprogram.models', function(require){
    "use strict";

    var models = require('point_of_sale.models');

    models.load_fields('account.journal', ['wechat']);

    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function(){
            var self = this;
            PosModelSuper.prototype.initialize.apply(this, arguments);
            this.bus.add_channel_callback("wechat.miniprogram", this.on_wechat_miniprogram, this);
            this.ready.then(function() {
                if (self.debug) {
                    var demo_message = {
                        'id': 666,
                        'note': 'Test Order Note',
                        'table_id': 1,
                        'customer_count': 4,
                        'state': 'done',
                        'line_ids': [{'id': 666, 'product_id': 69, 'price': 1, 'quantity': 5}],
                        'partner_id': 26,
                        'to_invoice': false,
                        'order_from_miniprogram': true
                    };
                    self.on_wechat_miniprogram(demo_message);
                }
            });
        },
        on_wechat_miniprogram: function(message) {
            var order = this.get('orders').find(function(item){
                return item.miniprogram_order_id === message.id;
            });
            if (order) {
                order.update_miniprogram_order(message);
            } else {
                this.create_miniprogram_order(message);
            }
        },
        create_miniprogram_order: function(data) {
            var self = this;

            var mp_data = {
                id: data.id,
                table_id: data.table_id,
                floors_id: data.floor_id,
                note: data.note,
                customer_count: data.customer_count,
                state: data.state,
                to_invoice: data.to_invoice,
                order_from_miniprogram: data.order_from_miniprogram
            };
            // get current order
            var current_order = this.get_order();
            // create new order
            var order = new models.Order({}, {mp_data: mp_data, pos: this});
            // get and set partner
            if(typeof data.partner_id === 'undefined') {
                order.set_client(null);
            } else {
                var client = order.pos.db.get_partner_by_id(data.partner_id);
                if(!client) {
                    $.when(this.load_new_partners_by_id(data.partner_id)).then(function(new_client){
                        new_client = order.pos.db.get_partner_by_id(data.partner_id);
                        order.set_client(new_client);
                    });
                }
                order.set_client(client);
            }

            this.get('orders').add(order);
            // set current order
            this.set('selectedOrder', current_order);
            // create orderlines
            data.line_ids.forEach(function(l){
                var product = self.db.get_product_by_id(l.product_id);
                if (product) {
                    var line = new models.Orderline({}, {pos: self, order: order, product: product});
                    if (l.quantity !== undefined && l.quantity !== line.quantity){
                        line.set_quantity(l.quantity);
                    }
                    if (l.price !== undefined && l.price !== line.price) {
                        line.set_unit_price(l.price);
                    }
                    order.orderlines.add(line);
                } else {
                    console.error("Product is not defined", product);
                }
            });
        },
        load_new_partners_by_id: function(partner_id){
            var self = this;
            var def = new $.Deferred();
            var fields = _.find(this.models,function(model){
                return model.model === 'res.partner';
            }).fields;
            var domain = [['id','=',partner_id]];
            rpc.query({
                    model: 'res.partner',
                    method: 'search_read',
                    args: [domain, fields],
                }, {
                    timeout: 3000,
                    shadow: true,
                }).then(function(partners){
                     // check if the partners we got were real updates
                    if (self.db.add_partners(partners)) {
                        def.resolve();
                    } else {
                        def.reject();
                    }
                }, function(type,err){
                    if (err) {
                        console.log(err);
                    }
                    def.reject();
                });
            return def;
        },
        get_mp_cashregister: function() {
            return this.cashregisters.find(function(c) {
                return c.journal.wechat && c.journal.wechat === 'jsapi';
            });
        }
    });

    var OrderSuper = models.Order;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            options = options || {};
            OrderSuper.prototype.initialize.apply(this, arguments);
            if (options.mp_data) {
                this.update_miniprogram_order(options.mp_data);
            }
        },
        update_miniprogram_order: function(data) {
            this.miniprogram_order_id = data.id;
            this.miniprogram_state = data.state;
            this.table = this.pos.tables_by_id[data.table_id];
            this.floor = this.table ? this.pos.floors_by_id[data.floor_id] : undefined;
            this.customer_count = data.customer_count || 1;
            this.note = data.note;
            this.to_invoice = data.to_invoice;
            this.order_from_miniprogram = data.order_from_miniprogram;
            // save to db
            this.trigger('change',this);
        },
        export_as_JSON: function() {
            var data = OrderSuper.prototype.export_as_JSON.apply(this, arguments);
            data.miniprogram_state = this.miniprogram_state;
            data.miniprogram_order_id = this.miniprogram_order_id;
            data.order_from_miniprogram = this.order_from_miniprogram;
            return data;
        },
        init_from_JSON: function(json) {
            this.miniprogram_state = json.miniprogram_state;
            this.miniprogram_order_id = json.miniprogram_order_id;
            this.order_from_miniprogram = json.order_from_miniprogram;
            OrderSuper.prototype.init_from_JSON.call(this, json);
        },
    });
});
