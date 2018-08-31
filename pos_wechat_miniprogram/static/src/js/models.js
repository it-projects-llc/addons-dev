/* Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
   License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_wechat_miniprogram.models', function(require){
    "use strict";

    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');

    models.load_fields('account.journal', ['wechat']);

    models.load_models({
        model: 'pos.miniprogram.order',
        fields: [],
        domain:[['confirmed_from_pos', '=', false]],
        loaded: function(self, orders) {
            var not_found = self.get('orders').map(function(r) {
                return r.miniprogram_order.id;
            });
            // load not confirmed orders
            orders.forEach(function(order) {
                not_found = _.without(not_found, order.id);
                order.lines_ids = [];
                self.get_miniprogram_order_lines_by_order_id(order.id).then(function(lines) {
                    if (Array.isArray(lines)) {
                        order.lines_ids = order.lines_ids.concat(lines);
                    } else {
                        order.lines_ids.push(lines);
                    }
                    self.on_wechat_miniprogram(order);
                });
            });
            // remove not found orders
            _.each(not_found, function(id) {
                var order = self.get('orders').find(function(r){
                    return id === r.miniprogram_order.id;
                });
                order.destroy({'reason':'abandon'});
            });
        },
    });

    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function() {
            PosModelSuper.prototype.initialize.apply(this, arguments);
            this.bus.add_channel_callback("wechat.miniprogram", this.on_wechat_miniprogram, this);
        },
        get_miniprogram_order_lines_by_order_id: function (id) {
            return rpc.query({
                model: 'pos.miniprogram.order.line',
                method: 'search_read',
                args: [[['order_id', '=', id]], []],
            });
        },
        on_wechat_miniprogram: function(message) {
            var order = this.get('orders').find(function(item){
                return item.miniprogram_order.id === message.id;
            });
            if (order) {
                this.update_miniprogram_order(order, message);
            } else {
                this.create_miniprogram_order(message);
            }
        },
        update_miniprogram_order: function(order, data) {
            var self = this;
            var not_found = order.orderlines.map(function(r) {
                return r.miniprogram_line.id;
            });

            data.lines_ids.forEach(function(l) {
                var line = order.orderlines.find(function(r){
                    // search by mini-program orderline id
                    return l.id === r.miniprogram_line.id;
                });

                not_found = _.without(not_found, l.id);

                if (line) {
                    // update line
                    line.apply_updates_miniprogram_line(l);
                } else {
                    // create new line and add to the Order
                    line = self.create_orderline_by_miniprogram_data(order, l);
                    if (line) {
                        order.orderlines.add(line);
                    }
                }
            });

            // remove old lines
            _.each(not_found, function(id){
                var line = order.orderlines.find(function(r){
                    return id === r.miniprogram_line.id;
                });
                order.orderlines.remove(line);
            });

            // update exist order
            order.apply_updates_miniprogram_order(data);
        },
        create_miniprogram_order: function(data) {
            var self = this;
            // get current order
            var current_order = this.get_order();
            // create new order
            var order = new models.Order({}, {mp_data: data, pos: this});
            // get and set partner
            if(typeof data.partner_id === 'undefined') {
                order.set_client(null);
            } else {
                var client = order.pos.db.get_partner_by_id(data.partner_id[0]);
                if(!client) {
                    $.when(this.load_new_partners_by_id(data.partner_id[0])).then(function(new_client){
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
            data.lines_ids.forEach(function(l) {
                var line = self.create_orderline_by_miniprogram_data(order, l);
                if (line) {
                    order.orderlines.add(line);
                }
            });
        },
        create_orderline_by_miniprogram_data: function(order, data) {
            var product = this.db.get_product_by_id(data.product_id[0]);
            if (product) {
                var line = new models.Orderline({}, {pos: this, order: order, product: product, mp_data: data});
                if (typeof data.quantity !== 'undefined' && data.quantity !== line.quantity){
                    line.set_quantity(data.quantity);
                }
                if (typeof data.price !== 'undefined' && data.price !== line.price) {
                    line.set_unit_price(data.price);
                }
                return line;
            }
            return false;
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
            this.miniprogram_order = {};
            OrderSuper.prototype.initialize.apply(this, arguments);
            if (options.mp_data) {
                this.apply_updates_miniprogram_order(options.mp_data);
            }
        },
        apply_updates_miniprogram_order: function(data) {
            // all mini-program data
            this.miniprogram_order = data;

            // common data for the order and for the order of mini-program
            this.table = this.pos.tables_by_id[data.table_id[0]];
            this.floor = this.pos.floors_by_id[data.floor_id[0]] || undefined;
            this.customer_count = data.customer_count || 1;
            this.note = data.note;
            this.to_invoice = data.to_invoice;

            // save to db
            this.trigger('change',this);
        },
        export_as_JSON: function() {
            var data = OrderSuper.prototype.export_as_JSON.apply(this, arguments);
            data.miniprogram_order = this.miniprogram_order;
            return data;
        },
        init_from_JSON: function(json) {
            this.miniprogram_order = json.miniprogram_order;
            OrderSuper.prototype.init_from_JSON.call(this, json);
        },
    });

    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options) {
            options = options || {};
            this.miniprogram_line = {};
            OrderlineSuper.prototype.initialize.apply(this,arguments);
            if (options.mp_data) {
                this.apply_updates_miniprogram_line(options.mp_data);
            }
        },
        apply_updates_miniprogram_line: function(data) {
            // all mini-program data
            this.miniprogram_line = data;

            // common data for the orderline and for the line of mini-program
            if (this.quantity !== data.quantity){
                this.set_quantity(data.quantity);
            }
            if (this.price !== data.price) {
                this.set_unit_price(data.price);
            }

            // save to db
            this.trigger('change',this);
            this.order.trigger('change',this);
        },
        export_as_JSON: function() {
            var data = OrderlineSuper.prototype.export_as_JSON.apply(this, arguments);
            data.miniprogram_line = this.miniprogram_line;
            return data;
        },
        init_from_JSON: function(json) {
            this.miniprogram_line = json.miniprogram_line;
            OrderlineSuper.prototype.init_from_JSON.call(this, json);
        },
    });
});
