/* Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */

odoo.define('pos_custom_orderline_popup.pos', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');

    models.load_fields('res.partner', ['gender', 'birthdate_date', 'surname', 'fathers_name']);

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

    var orderline_customzation = screens.ActionButtonWidget.extend({
        template: 'orderline_customzation_button',
        button_click: function(){
            var self = this;
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            if (orderlines.length && order.get_selected_orderline()) {
                this.gui.show_popup('orderline_customzation',{
                    'title': 'orderline_customzation',
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
                this.update_partner_fields(sol.partner_id);
                this.$el.find('.partner_id').val(sol.partner_id);
                this.update_users_fields(sol.executor_id, sol.seller_id);
            }

            this.$el.find('select.partner_id').on('change', function() {
                if (this.value) {
                    self.update_partner_fields(this.value);
                }
            });

//            this.$el.find('.button.copy').on('click', function() {
//                self.take_previous_line_values();
//            });
        },

//        take_previous_line_values: function() {
//            var sol = this.selected_orderline;
//            var ols = sol.order.get_orderlines();
//            var ol_ids = _.chain(ols)
//            .pluck('id')
//            .filter(function(el){
//                return el < sol.id;
//            }).value();
//            var previous_ol = _.find(ols, function(ol){
//
//            });
//
//
//            var orderlines = sol.order.get_orderlines()ж
//
//            var length = sol.order.get_orderlines().length
//            while (!previous_ol || i > 0) {
//              i--;
//              previous_ol = _.find(sol.order.get_orderlines(), function() {
//                return
//              });
//            }
//        },

        update_partner_fields: function(partner_id) {
            var partner = this.pos.db.get_partner_by_id(partner_id)
            this.$el.find('.name').val(partner.name);
            this.$el.find('.gender').val(partner.gender);
            this.$el.find('.surname').val(partner.surname);
            this.$el.find('.fathers_name').val(partner.fathers_name);
            this.$el.find('.birthday_date').val(partner.birthdate_date);
        },

        update_users_fields: function(executor_id, seller_id) {
            this.$el.find('.seller_id').val(seller_id);
            this.$el.find('.executor_id').val(executor_id);
        },

        click_confirm : function(event) {
            var data = {
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
            }

            this.selected_orderline.set_customized_data(data);
            this.gui.close_popup();
            if (this.options.confirm) {
                this.options.confirm.call(self,data);
            }
        },

    });
    gui.define_popup({name:'orderline_customzation', widget: orderline_customzation});

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        set_customized_data: function(data) {
            var self = this;
            _.chain(data)
            .keys()
            .intersection(['seller_id', 'executor_id', 'partner_id', 'partner_vals'])
            .each(function(k) {
                self[k] = data[k];
            });
            console.log('asdsad');
        },

        export_as_JSON: function() {
            var data = _super_orderline.export_as_JSON.apply(this, arguments);
            return _.extend(data, {
                'seller_id': this.seller_id,
                'partner_id': this.partner_id,
                'executor_id': this.executor_id,
                'partner_vals': this.partner_vals,
            });
        },

        init_from_JSON: function(json) {
            _super_orderline.init_from_JSON.call(this, json);
            this.set_customized_data(json);
        },
    });





    var core = require('web.core');

    var utils = require('web.utils');
    var rpc = require('web.rpc');

    var QWeb = core.qweb;
    var _t = core._t;
    var round_pr = utils.round_precision;



});
