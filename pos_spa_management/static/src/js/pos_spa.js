/* Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_spa_management', function(require){

    var screens = require('pos_restaurant_base.screens');
    var models = require('pos_restaurant_base.models');
    var PopupWidget = require('point_of_sale.popups');
    var floors = require('pos_restaurant.floors');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;

    models.load_fields('product.product',['duration']);

    screens.ActionpadWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.set-customer').off().click(function(){
                self.gui.show_popup('client_popup', {});
            });
        },
    });

    var ClientSelectionPopup = PopupWidget.extend({
        template:'ClientSelectionPopup',
        show: function(options){
            this._super(options);
            var self = this;
            var inputs = self.$el.find('input');
            this.$el.find('.btn-primary').off().on('click', function(ev){
                self.request_get_name_by_phone(inputs[0].value).done(function(res){
                    if (res) {
                        inputs[1].value = res[1];
                        self.client = self.pos.db.get_partner_by_id(res[0]);
                    } else {
                        self.client = false;
                        inputs[1].placeholder = 'Client not found';
                    }
                }).fail(function(res) {
                    self.client = false;
                    inputs[1].placeholder = 'Client not found';
                });
            });
        },

        request_get_name_by_phone: function(phone) {
            var self = this;
            return rpc.query({
                model: 'res.partner',
                method: 'get_name_by_phone',
                args: [phone],
            });
        },

        click_confirm: function() {
            if (this.client) {
                this.pos.get_order().set_client(this.client);
            } else {
                var inputs = this.$el.find('input');
                if (inputs[0].value && inputs[1].value) {
                    this.create_new_customer(inputs[0].value, inputs[1].value);
                }
            }
            this.gui.close_popup();
        },

        create_new_customer: function(phone, name) {
            var self = this;

            rpc.query({
                model: 'res.partner',
                method: 'create_from_ui',
                args: [{
                    name: name,
                    phone: phone,
                    id: false,
                    country_id: false,
                    property_product_pricelist: false,
                }],
            }).then(function(partner_id){
                self.gui.screen_instances.clientlist.reload_partners().then(function(res){
                    var pos = self.pos;
                    var new_partner = self.pos.db.get_partner_by_id(partner_id);
                    pos.get_order().set_client(new_partner);
                });
            },function(err,ev){
                ev.preventDefault();
                var error_body = _t('Your Internet connection is probably down.');
                if (err.data) {
                    var except = err.data;
                    error_body = except.arguments && except.arguments[0] || except.message || error_body;
                }
                self.gui.show_popup('error',{
                    'title': _t('Error: Could not Save Changes'),
                    'body': error_body,
                });
            });
        },
    });
    gui.define_popup({name:'client_popup', widget: ClientSelectionPopup});

    screens.PaymentScreenWidget.include({
        finalize_validation: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            var table = order.table;
            table.duration = this.total_order_duration() * 60 * 1000;
            table.start_time = new Date().getTime();
            table.last_order_name = order.name;
            if (this.gui.screen_instances.receipt.should_close_immediately()){
                this.gui.screen_instances.receipt.click_next();
            } else {
                this.gui.screen_instances.receipt.click_next();
            }
        },

        total_order_duration: function(){
            return _.chain(this.pos.get_order().get_orderlines()).
                map(function(ol){
                    return ol.product.duration * ol.get_quantity();
                }).
                reduce(function(memo, num){
                    return memo + num;
                }, 0).value();
        },
    });

    floors.TableWidget.include({
        renderElement: function(){
            this._super();

            var element = this.$el.find('.table-seats')[0];
            if (!this.table.duration) {
                element.textContent = '';
                return;
            }
            var current_time = new Date().getTime();
            if (this.check_table_availability()) {
                var duration = 0;
            } else {
                var time_left = this.table.duration - (current_time - this.table.start_time);
                this.start_spa_timer(parseInt(time_left/1000), element);
            }
        },

        start_spa_timer(duration, element) {
            var timer = duration, minutes, seconds;
            var self = this;
            this.countdown_timer = setInterval(function () {
                minutes = parseInt(timer / 60, 10);
                seconds = parseInt(timer % 60, 10);

                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;

                element.textContent = minutes + ":" + seconds;

                if ((minutes === 15 || minutes === '00') && seconds === '00') {
                    self.gui.play_sound('error')
                }

                if (--timer < 0) {
                    timer = duration;
                }
            }, 1000);
        },

        check_table_availability: function(){
            var table = this.table;
            var current_time = new Date().getTime();
            if (!table.duration || !table.start_time || (table.duration + table.start_time < current_time)) {
                return true;
            }
            return false;
        },

        click_handler: function(){
            var self = this;
            var floorplan = this.getParent();
            if (floorplan.editing) {
                return this._super();
            }

            var table = this.table;
            if (!table || this.check_table_availability()) {
                return this._super();
            }

            return this.gui.show_popup('confirm',{
                'title': _t('Can not open the Table'),
                'body': _t('The room is occupied. Click `Confirm` if you want to change the executor'),
                'confirm': function () {
                    self.gui.select_user().done(function(user){
                        return self.change_executor(user.id);
                    });
                },
            });
        },

        change_executor: function(user_id) {
            return rpc.query({
                model: 'pos.order',
                method: 'change_executor',
                args: [user_id, this.table.last_order_name],
            });
        },
    });

});
