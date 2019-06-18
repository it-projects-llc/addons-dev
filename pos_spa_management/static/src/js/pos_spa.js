/* Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_spa_management', function(require){

    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var PopupWidget = require('point_of_sale.popups');
    var floors = require('pos_restaurant.floors');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;

    models.load_fields('product.product',['duration']);

    var ConfirmPopupWidgetInherited = PopupWidget.extend({
        template: 'ConfirmPopupWidgetInherited',
        show: function(options){
            this._super(options);
            var self = this;
            this.$el.find('.third').on('click', function(){
                self.click_third();
            });
        },

        click_third: function(){
            this.gui.close_popup();
            if (this.options.third) {
                this.options.third.call(this);
            }
        },
    });
    gui.define_popup({name:'confirm_triple', widget: ConfirmPopupWidgetInherited});


    screens.ActionpadWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);

            this.pos.bind('change:referrer', function() {
                self.renderElement();
            });
        },

        renderElement: function() {
            var self = this;
            this._super();
            this.$('.set-customer').off().click(function(){
                self.gui.show_popup('client_popup', {
                    mode: 'client',
                });
            });
            this.$('.set-referrer').off().click(function(){
                self.gui.show_popup('client_popup', {
                    mode: 'referrer',
                });
            });
        },
    });

    var ClientSelectionPopup = PopupWidget.extend({
        template:'ClientSelectionPopup',
        show: function(options){
            this._super(options);
            var self = this;
            this.client = false;
            var inputs = self.$el.find('input');
            this.$el.find('.btn-primary').off().on('click', function(ev){
                self.request_get_name_by_phone(inputs[0].value).done(function(res){
                    if (res) {
                        inputs[1].value = res[1];
                        self.client = self.pos.db.get_partner_by_id(res[0]);
                    } else {
                        self.action_request_failed();
                    }
                }).fail(function(res) {
                    self.action_request_failed();
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
            var self = this;
            if (this.client) {
                this.action_confirm();
            }
            this.request_get_name_by_phone(this.$el.find('input')[0].value).done(function(res){
                if (res) {
                    self.client = self.pos.db.get_partner_by_id(res[0]);
                    self.action_confirm();
                } else {
                    self.action_request_failed();
                }

            }).fail(function(){
                self.action_request_failed();
            });
        },

        action_request_failed: function() {
            this.client = false;
            this.$el.find('input')[1].placeholder = 'Client not found';
        },

        action_confirm: function () {
            if (this.client && this.check_referrer_mode()) {
                this.pos.get_order().set_referrer(this.client);
            } else if (this.client) {
                this.pos.get_order().set_client(this.client);
            } else {
                var inputs = this.$el.find('input');
                if (inputs[0].value && inputs[1].value) {
                    this.create_new_customer(inputs[0].value, inputs[1].value);
                }
            }
            this.gui.close_popup();
        },

        check_referrer_mode: function() {
            return this.options.mode && this.options.mode == 'referrer';
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
                    if (self.check_referrer_mode()) {
                        pos.get_order().set_referrer(new_partner);
                    } else {
                        pos.get_order().set_client(new_partner);
                    }
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

    var PosModelSuper = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        set_referrer: function(partner) {
            this.get_order().referrer = partner;
        },

        get_referrer: function() {
            return this.get_order()
            ? this.get_order().get_referrer()
            : false;
        },

        save_timer: function(table) {
            localStorage['table_' + table.id] = JSON.stringify({
                'duration': table.duration,
                'start_time': table.start_time,
                'executors': table.executors,
                'last_order_name': table.last_order_name,
            });
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_as_JSON: function() {
            var data = _super_order.export_as_JSON.apply(this, arguments);
            data.referrer_id = this.pos.get_referrer().id;
            data.beyond_timer_addition = this.beyond_timer_addition;
            return data;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.call(this, json);
            this.set_referrer(json.referrer_id);
            this.beyond_timer_addition = json.beyond_timer_addition;
        },
        set_referrer: function(partner) {
            this.referrer = partner;
            this.pos.trigger('change:referrer');
        },

        get_referrer: function() {
            return this.referrer || false;
        },

        get_executors: function() {
            return _.chain(this.get_orderlines())
                .pluck('ms_info').pluck('created').pluck('user').pluck('id')
                .uniq().value();
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        export_as_JSON: function() {
            var data = _super_orderline.export_as_JSON.apply(this, arguments);
            if (this.ms_info && this.ms_info.created) {
                data.user_id = this.ms_info.created.user.id;
            }
            return data;
        },
    });

    screens.PaymentScreenWidget.include({
        finalize_validation: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            if (order && !order.beyond_timer_addition) {
                var table = order.table;
                table.duration = this.total_order_duration() * 60 * 1000;
                table.start_time = new Date().getTime();
                table.last_order_name = order.name;
                table.executors = order.get_executors();
                this.pos.save_timer(table);
                if (this.gui.screen_instances.receipt.should_close_immediately()){
                    this.gui.screen_instances.receipt.click_next();
                }
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

        renderElement: function() {
            var self = this;
            this._super();

            this.$('.js_set_customer').off().hide().click(function(){
                self.gui.show_popup('client_popup', {
                    mode: 'client',
                });
            });
        },
    });

    floors.TableWidget.include({
        init: function(parent, options){
            this._super(parent, options);
            var saved_data = localStorage['table_' + options.table.id];
            if (!saved_data) {
                return;
            }
            saved_data = JSON.parse(saved_data);
            var duration = saved_data.duration;
            if (!saved_data.duration || saved_data.start_time + saved_data.duration <= this.get_current_time()) {
                return;
            }
            this.table.start_time = saved_data.start_time;
            this.table.duration = saved_data.duration;
            this.table.executors = saved_data.executors;
            this.table.last_order_name = saved_data.last_order_name;
            var time_left = this.table.duration - (this.get_current_time() - this.table.start_time);
            // this.start_spa_timer(time_left);
        },

        get_current_time: function() {
            return new Date().getTime();
        },

        renderElement: function(){
            this._super();

            var element = this.$el.find('.table-seats')[0];
            if (!this.table.duration) {
                element.textContent = '';
                return;
            }

            if (this.check_table_availability()) {
                var duration = 0;
            } else {
                var time_left = this.table.duration - (this.get_current_time() - this.table.start_time);
                this.render_play_buttons();
                this.start_spa_timer(parseInt(time_left/1000));
            }
        },

        start_spa_timer(duration) {
            var element = this.$el.find('.table-seats')[0];
            element.textContent = '';
            var timer = duration, minutes, seconds;
            var self = this;
            this.countdown_timer = setInterval(function () {
                minutes = parseInt(timer / 60, 10);
                seconds = parseInt(timer % 60, 10);

                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;

                element.textContent = minutes + ":" + seconds;

                if (!this.stopped_timer && (minutes === 15 || minutes === '00') && seconds === '00') {
                    self.gui.play_sound('error')
                }

                if (minutes === '00' && seconds === '00') {
                    self.remove_timer();
                    this.stopped_timer = true;
                }

                if (--timer < 0) {
                    timer = duration;
                }
            }, 1000);
        },

        remove_timer: function() {
            clearInterval(this.countdown_timer);
            this.countdown_timer = false;
            var element = this.$el.find('.table-seats')[0];
            element.textContent = '';
        },

        render_play_buttons: function (visible) {
            var self = this;
            var $label = this.$el.find('.label');
            $label[0].innerHTML += ' <i class="fa fa-pause"></i> <i class="fa fa-play"></i>';
            $label.find('i.fa-pause').off().hide().on('click', function(ev) {
                ev.stopPropagation();
                self.click_pause(ev);
            });
            $label.find('i.fa-play').off().hide().on('click', function(ev) {
                ev.stopPropagation();
                self.click_play(ev);
            });
        },

        click_pause: function(ev) {
            this.time_left = this.table.duration - (this.get_current_time() - this.table.start_time);
            this.remove_timer();
            this.$el.find('i.fa-pause').hide();
            this.$el.find('i.fa-play').show();
        },

        click_play: function(ev) {
            this.table.start_time = new Date().getTime();
            this.table.duration = this.time_left;
            this.start_spa_timer(parseInt(this.time_left/1000));
            this.$el.find('i.fa-play').hide();
            this.pos.save_timer(this.table);
            // this.$el.find('i.fa-pause').show();
        },

        check_table_availability: function(){
            var table = this.table;
            if (!table.duration || !table.start_time || (table.duration + table.start_time < this.get_current_time())) {
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
            var super_method = self._super;
            return this.gui.show_popup('confirm_triple', {
                'title': _t('Can not open the Table'),
                'body': _t('The room is occupied. Click `Confirm` if you want to change the executor. Click `Add Order` if you want to sell non-durable products'),
                'confirm': function () {
                    self.click_pause();
                    self.gui.select_changed_executor(table).done(function(previous_user_id){
                        return self.gui.select_user().done(function(user){
                            table.executors.push(user.id);
                            table.executors = _.chain(table.executors)
                            .reject(function(uid){
                                return previous_user_id.id == uid;
                            })
                            .uniq().value();
                            self.pos.save_timer(table);
                            return self.change_executor(user.id, previous_user_id.id);
                        });
                    });
                },
                'third': function () {
                    _.bind(super_method, self)()
                    this.pos.get_order().beyond_timer_addition = true;
                    return;
                },
            });
        },

        change_executor: function(user_id, previous_user_id) {
            return rpc.query({
                model: 'pos.order',
                method: 'change_executor',
                args: [user_id, this.table.last_order_name, previous_user_id],
            });
        },
    });


    gui.Gui.include({
        select_changed_executor: function(table){
            var self = this;
            var def  = new $.Deferred();

            var list = _.map(table.executors, function(uid) {
                var user = _.find(self.pos.users, function(u) {
                    return uid === u.id;
                });
                return {
                    'label': user.name,
                    'item':  user,
                }
            });

            this.show_popup('selection',{
                title: _t('Select Current Executor'),
                list: list,
                confirm: function(user){
                    def.resolve(user);
                },
                cancel: function(){
                    def.reject();
                },
                is_selected: function(user){ return user === self.pos.get_cashier(); },
            });

            return def.then(function(user){
                return user;
            });
        },
    });
});
