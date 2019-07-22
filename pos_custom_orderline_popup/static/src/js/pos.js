/* Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */

odoo.define('pos_custom_orderline_popup.pos', function (require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;

    models.load_fields('res.partner', ['gender', 'birthday_date', 'surname', 'fathers_name']);

    models.load_models({
        model: 'guest.category',
        fields: ['name'],
        loaded: function(self, categories) {
            self.db.guest_categories = categories;
        },
    });
    models.load_models({
        model: 'service.room',
        fields: ['name'],
        loaded: function(self, rooms) {
            self.db.service_rooms = rooms;
        },
    });

    var mandatory_popup_fields = [
        'p_name', 'partner_id', 'partner_vals',
        'seller_id', 'executor_id',
        'service_room_id', 'guest_category_id'
    ];

    var orderline_customzation = screens.ActionButtonWidget.extend({
        template: 'orderline_customzation_button',
        button_click: function(){
            var self = this;
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            if (orderlines.length && order.get_selected_orderline()) {
                this.gui.show_popup('orderline_customzation',{
                    'title': 'Add Info to Orderline',
                });
            }
        },
    });
    screens.define_action_button({
        'name': 'orderline_customzation',
        'widget': orderline_customzation,
    });

    var orderline_customzation = PopupWidget.extend({
        template: 'orderline_customzation_popup',
        show: function(options){
            this._super(options);
            var self = this;
            var order = this.pos.get_order();
            this.selected_orderline = order.get_selected_orderline();
            var sol = this.selected_orderline;
            if (sol && sol.partner_id) {
                this.update_all_fields(sol);
            }

            this.$el.find('select.partner_id').on('change', function() {
                if (this.value) {
                    self.update_partner_fields(this.value);
                }
            });

            this.$el.find('.button.copy').on('click', function() {
                var orderline = self.take_previous_orderline();
                self.update_all_fields(orderline);
            });
        },

        take_previous_orderline: function() {
            var orderline = false;
            for (var i = this.selected_orderline.id - 1; i > 0 ; i -= 1) {
                orderline = this.pos.get_order().get_orderline(i);
                if (orderline) {
                    return orderline;
                }
            }
        },

        update_db_partner: function(data) {
            var partner_id = data.partner_id;
            var self = this;
            var  done = new $.Deferred();

            if (!partner_id && data.partner_vals) {
                // prevents errors in backend due to inproper date
                data.partner_vals.birthday_date = data.partner_vals.birthday_date || false;
            }

            if (!partner_id && data.partner_vals && data.partner_vals.name) {
                rpc.query({
                    model: 'res.partner',
                    method: 'create_from_ui',
                    args: [data.partner_vals],
                })
                .then(function(new_partner_id){
                    self.gui.screen_instances.clientlist.saved_client_details(new_partner_id).then(function(res) {
                        partner_id = new_partner_id;
                        done.resolve();
                    });
                },function(err, ev){
                    console.log(err, ev);
                });
            } else {
                done.resolve();
            }

            return done.then(function(res) {
                if (!partner_id) {
                    return;
                }
                data.partner_id = partner_id;
                partner_id = self.pos.db.get_partner_by_id(partner_id);
                var updated_keys = _.chain(data.partner_vals)
                    .keys()
                    .filter(function(key) {
                        return data.partner_vals[key];
                    }).value();
                if (updated_keys.length) {
                    partner_id = _.extend(
                        partner_id,
                        _.pick(data.partner_vals, ...updated_keys)
                     );
                }
                return data;
            });
        },

        update_partner_fields: function(partner_id) {
            var partner = this.pos.db.get_partner_by_id(partner_id);
            if (!partner) {
                return;
            }
            this.$el.find('.name').val(partner.name);
            this.$el.find('.surname').val(partner.surname);
            this.$el.find('.fathers_name').val(partner.fathers_name);
            this.$el.find('.birthday_date').val(partner.birthday_date);
            this.$el.find('.gender.' + partner.gender)[0].checked = true;
        },

        update_all_fields: function(orderline) {
            if (!orderline) {
                return;
            }
            this.update_partner_fields(orderline.partner_id);
            this.$el.find('.seller_id').val(orderline.seller_id);
            this.$el.find('.partner_id').val(orderline.partner_id);
            this.$el.find('.executor_id').val(orderline.executor_id);
            this.$el.find('.service_room_id').val(orderline.service_room_id);
            this.$el.find('.guest_category_id').val(orderline.guest_category_id);
        },

        click_confirm : function(event) {
            var all_inputs = this.$el.find('input, select');
            all_inputs.removeClass('alert');
            var data = {
                p_name: this.$el.find('.name').val(),
                partner_vals: {
                    name: this.$el.find('.name').val(),
                    gender: this.$el.find('.gender').val(),
                    surname: this.$el.find('.surname').val(),
                    fathers_name: this.$el.find('.fathers_name').val(),
                    birthday_date: this.$el.find('.birthday_date').val(),
                },
                seller_id: this.$el.find('.seller_id').val(),
                partner_id: this.$el.find('.partner_id').val(),
                executor_id: this.$el.find('.executor_id').val(),
                service_room_id: this.$el.find('.service_room_id').val(),
                guest_category_id: this.$el.find('.guest_category_id').val(),
            }

            var not_filled_fields = this.not_filled_fields(data);
            if(not_filled_fields.length) {
                this.$el.find('input, select').filter('.' + not_filled_fields.join(',.')).addClass('alert');
                return not_filled_fields;
            }

            var self = this;
            return this.update_db_partner(data).then(function(res) {
                self.selected_orderline.set_customized_data(res);
                self.gui.close_popup();
                if (self.options.confirm) {
                    self.options.confirm.call(self,data);
                }
            });
        },

        not_filled_fields: function(data) {
            var filled_fields = _.chain(data)
                .keys()
                .filter(function(key) {
                    return data[key];
                }).value();
            if (filled_fields.length) {
                var not_filled_fields = _.without(mandatory_popup_fields, ...filled_fields, 'partner_id');
                return not_filled_fields;
            }
            return [];
        },

    });
    gui.define_popup({name:'orderline_customzation', widget: orderline_customzation});

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({

        set_customized_data: function(data) {
            var self = this;
            _.chain(data)
            .keys()
            .intersection(mandatory_popup_fields)
            .each(function(k) {
                self[k] = data[k];
            });
        },

        get_orderline_partner_data: function() {
            return {
                'p_name': this.p_name,
                'seller_id': this.seller_id,
                'partner_id': this.partner_id,
                'executor_id': this.executor_id,
                'partner_vals': this.partner_vals,
                'service_room_id': this.service_room_id,
                'guest_category_id': this.guest_category_id,
            };
        },

        export_as_JSON: function() {
            var data = _super_orderline.export_as_JSON.apply(this, arguments);
            return _.extend(data, this.get_orderline_partner_data());
        },

        init_from_JSON: function(json) {
            _super_orderline.init_from_JSON.call(this, json);
            this.set_customized_data(json);
        },

        not_filled_fields: function() {
            var data = this.get_orderline_partner_data();
            return _.without(mandatory_popup_fields, ..._.chain(data)
                .keys()
                .filter(function(key) {
                    return data[key];
                }).value()
            );
        },
    });

    var OrderSuper = models.Order;
    models.Order = models.Order.extend({
        check_orderlines_data: function(){
            return _.find(this.get_orderlines(), function(ol) {
                return ol.not_filled_fields().length
            });
        },
    });

    screens.ActionpadWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            var button_pay_click_handler = $._data(this.$el.find(".button.pay")[0],"events").click[0].handler;
            this.$('.pay').off('click').click(function(){
                if (!self.pos.get_order().check_orderlines_data()) {
                    return button_pay_click_handler();
                }
                return self.gui.show_popup('error', {
                    title: _t('Unable to Proceed'),
                    body: _t('Some orderlines data is not filled'),
                });
            });
        },
    });

});
