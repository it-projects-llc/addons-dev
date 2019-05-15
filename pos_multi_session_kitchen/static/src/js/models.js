odoo.define('pos_multi_session_kitchen.models', function(require){

    var multi_session = require('pos_multi_session');
    var core = require('web.core');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var session = require('web.session');

    var _t = core._t;

//    // load all kitchens
//    models.load_models({
//        model: 'pos.config',
//        fields: ['cat_ids'],
//        domain: [['screen','=','kitchen']],
//        loaded: function(self, kitchens){
//            self.kitchens = kitchens;
//        },
//    });

    // load all order tags
    models.load_models({
        model: 'pos.order.tag',
        fields: ['name', 'technical_name', 'priority', 'name_color', 'background_color'],
        loaded: function(self, tags){
            self.order_tags = tags;
        },
    });

    // load all order buttons
    models.load_models({
        model: 'pos.order.button',
        fields: ['name', 'background_color', 'name_color', 'next_tag_id', 'remove_tag_id'],
        loaded: function(self, buttons){
            self.order_buttons = buttons;
        },
    });

    // load all line states
    models.load_models({
        model: 'pos.order.line.state',
        fields: ['name', 'technical_name', 'type', 'sequence', 'show_in_kitchen', 'show_for_waiters', 'sound_signal'],
        loaded: function(self, res){
            var sorting_states = function(idOne, idTwo) {
                return idOne.sequence - idTwo.sequence;
            };
            if (res) {
                self.states = res.sort(sorting_states);
            }
        },
    });

    // load all line buttons
    models.load_models({
        model: 'pos.order.line.button',
        fields: ['name', 'background_color', 'name_color', 'show_for_waiters', 'show_in_kitchen', 'next_state_id', 'condition_code', 'action_close'],
        loaded: function(self, buttons){
            self.line_buttons = buttons;
        },
    });

    // load all category settings
    models.load_models({
        model: 'pos.kitchen.category.settings',
        fields: ['name', 'button_ids', 'state_ids'],
        loaded: function(self, settings){
            self.category_settings = settings;
        },
    });

    models.load_fields('pos.category', ['settings_id']);

    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        ms_on_update: function(message, sync_all) {
            PosModelSuper.prototype.ms_on_update.apply(this, arguments);
            var data = message.data || {};
            var order = false;
            if (data.uid) {
                order = this.get('orders').find(function(item){
                    return item.uid === data.uid;
                });
            }
            this.trigger('change:kitchen', order, data.uid);
        },
        get_state_by_id: function(id) {
            return this.states.find(function(state){
                return state.id === id;
            });
        },
        get_kitchen_button_by_id: function(id) {
            return this.line_buttons.find(function(button){
                return button.id === id;
            });
        },
        get_category_settings_by_id: function(id) {
            return this.category_settings.find(function(settings){
                return settings.id === id;
            });
        },
        on_removed_order: function(removed_order,index,reason){
            if (removed_order) {
                // stop timer and save stop datetime
                var lines = removed_order.get_orderlines();
                lines.forEach(function(line) {
                    line.stop_timer();
                });
            }
            return PosModelSuper.prototype.on_removed_order.apply(this, arguments);
        },
        get_order_buttons_by_id: function(id){
            return this.order_buttons.find(function(button){
                return button.id === id;
            });
        },
        get_order_tags_by_id: function(id){
            return this.order_tags.find(function(tag) {
                return tag.id === id;
            });
        }
    });

    var OrderSuper = models.Order;
    models.Order = models.Order.extend({
        initialize: function(){
            this.tags = [];
            this.priority = 0;
            OrderSuper.prototype.initialize.apply(this, arguments);
        },
        set_tag: function(tag) {
            var exist_tag = this.tags.find(function(current_tag) {
                return current_tag.id === tag.id;
            });
            if (exist_tag) {
                this.remove_tag(exist_tag);
                return false;
            }
            this.tags.push(tag);
            this.change_priority();
            this.trigger('change', this);
            this.trigger('change:sync');
            if (this.pos.gui.screen_instances.products) {
                this.pos.gui.screen_instances.products.order_widget.renderElement(true);
            }
        },
        remove_tag: function(tag) {
            var exist_tag = this.tags.find(function(current_tag) {
                return current_tag.id === tag.id;
            });
            if (exist_tag) {
                var index = this.tags.indexOf(exist_tag);
                this.tags.splice(index, 1);
                this.change_priority();
                this.trigger('change', this);
                this.trigger('change:sync');
                if (this.pos.gui.screen_instances.products) {
                    this.pos.gui.screen_instances.products.order_widget.renderElement(true);
                }
            }
        },
        change_priority: function() {
            var sum = 0;
            var tags = this.get_tags();
            tags.forEach(function(tag) {
                sum += tag.priority;
            });
            this.priority = sum;
        },
        get_priority: function() {
            return this.priority;
        },
        get_tags: function() {
            return this.tags || [];
        },
        export_as_JSON: function() {
            var data = OrderSuper.prototype.export_as_JSON.apply(this, arguments);
            data.tags = this.tags;
            data.priority = this.priority;
            return data;
        },
        init_from_JSON: function(json) {
            this.tags = json.tags;
            this.priority = json.priority;
            OrderSuper.prototype.init_from_JSON.call(this, json);
        },
        apply_ms_data: function(data) {
            // This methods is added for compatibility with module https://www.odoo.com/apps/modules/10.0/pos_multi_session/
            /* It is necessary to check the presence of the super method
            in order to be able to inherit the apply_ms_data
            without calling require('pos_multi_session')
            and without adding pos_multi_session in dependencies in the manifest.

            At the time of loading, the super method may not exist. So, if the js file is loaded
            first among all inherited, then there is no super method and it is not called.
            If the file is not the first, then the super method is already created by other modules,
            and we call super method. */
            if (OrderSuper.prototype.apply_ms_data) {
                OrderSuper.prototype.apply_ms_data.apply(this, arguments);
            }
            this.tags = data.tags;
            this.priority = data.priority;
            if (this.pos.gui.screen_instances.products) {
                this.pos.gui.screen_instances.products.order_widget.renderElement(true);
            }
        }
    });

    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        initialize: function() {
            this.states = [];
            this.line_buttons = [];
            OrderlineSuper.prototype.initialize.apply(this, arguments);
            if (!this.states.length && !this.line_buttons.length) {
                this.init_category_data();
            }
        },
        can_be_merged_with: function(orderline){
            // orderline with a different state cannot be merged
            if (this.current_state && orderline.current_state && this.current_state.id !== orderline.current_state.id) {
                return false;
            }
            OrderlineSuper.prototype.can_be_merged_with.apply(this, arguments);
        },
        init_category_data: function() {
            var self = this;
            if (this.product) {
                var category = this.pos.db.category_by_id[this.product.pos_categ_id[0]];
                if (category) {
                    var settings = this.pos.get_category_settings_by_id(category.settings_id[0]);

                    // TODO: do not copy the states
                    // init states
                    settings.state_ids.forEach(function(id) {
                        self.states.push(Object.assign({}, self.pos.get_state_by_id(id)));
                    });

                    // set current state (the first state, all states are sorted by sequence field)
                    this.set_state(Object.assign({}, this.pos.get_state_by_id(settings.state_ids[0])));

                    // init buttons
                    settings.button_ids.forEach(function(id) {
                        self.line_buttons.push(self.pos.get_kitchen_button_by_id(id));
                    });
                }
            }
        },
        export_as_JSON: function() {
            var data = OrderlineSuper.prototype.export_as_JSON.apply(this, arguments);
            data.current_state = this.current_state;
            data.states = this.states;
            return data;
        },
        init_from_JSON: function(json) {
            this.current_state = json.current_state;
            this.states = json.states;
            OrderlineSuper.prototype.init_from_JSON.call(this, json);
        },
        set_state: function(state) {
            if (this.current_state) {
                this.stop_timer();
            }
            var active_state = this.states.find(function(current_state){
                return state.id === current_state.id;
            });
            active_state.active = true;
            // current timer status
            active_state.run_timer = true;

            this.current_state = active_state;

            this.start_timer();

            this.trigger('change', this);
            this.order.trigger('change:sync');
        },
        action_close: function() {
            if (this.current_state) {
                this.stop_timer();
                this.current_state.stop_timer_date = false;
                this.current_state.run_timer_date = false;

                // hide timer and buttons
                this.current_state.action_close = true;

                this.trigger('change', this);
                this.order.trigger('change:sync');
            }
        },
        start_timer: function() {
            var self = this;
            if (this.current_state && this.current_state.run_timer) {
                if (this.current_state.run_timer_date) {
                    // stop current timer
                    this.stop_timer();
                    this.current_state.run_timer = true;

                    var run_timer_date = this.current_state.run_timer_date;
                    this.update_timer(run_timer_date);

                    this.stateTimer = setInterval(function(){
                        self.update_timer(run_timer_date);
                    }, 1000);
                } else {
                    // Set a date and get the milliseconds
                    var date = new Date();
                    var dateMsec = date.getTime();
                    this.current_state.run_timer_date = dateMsec;
                    this.start_timer();
                }
            } else {
                this.stop_timer();
            }
        },
        stop_timer: function() {
            if (this.current_state) {
                // Set a date and get the milliseconds
                var date = new Date();
                var dateMsec = date.getTime();
                clearInterval(this.stateTimer);
                this.current_state.run_timer = false;
                this.current_state.stop_timer_date = dateMsec;
            }
        },
        get_formatted_time: function(run_timer_date) {
            var self = this;

            // Set a date and get the milliseconds
            var date = new Date();
            var dateMsec = date.getTime();

            // Get the difference in milliseconds.
            var interval = dateMsec - run_timer_date;

            // Set the unit values in milliseconds.
            var msecPerMinute = 1000 * 60;
            var msecPerHour = msecPerMinute * 60;
            var msecPerDay = msecPerHour * 24;

            // Calculate how many days the interval contains. Subtract that
            // many days from the interval to determine the remainder.
            var days = Math.floor(interval / msecPerDay );
            interval -= (days * msecPerDay );

            // Calculate the hours, minutes, and seconds.
            var hours = Math.floor(interval / msecPerHour );
            interval -= (hours * msecPerHour );

            var minutes = Math.floor(interval / msecPerMinute );
            interval -= (minutes * msecPerMinute );

            var seconds = Math.floor(interval / 1000 );

            function zeroPadding(num, digit) {
                var zero = '';
                for(var i = 0; i < digit; i++) {
                    zero += '0';
                }
                return (zero + num).slice(-digit);
            }
            var time = '';
            if (days !== 0) {
                time = days + ' days ';
            }
            time += zeroPadding(hours, 2) + ':' + zeroPadding(minutes, 2) + ':' + zeroPadding(seconds, 2);

            return time;
        },
        update_timer: function(run_timer_date) {
            var time = this.get_formatted_time(run_timer_date);

            if (this.waiters_timer) {
                this.waiters_timer.html(time);
            }
            if (this.kitchen_timer) {
                this.kitchen_timer.html(time);
            }
        },
        get_active_states: function(){
            return this.states.filter(function(state) {
                return state.active;
            });
        },
        apply_ms_data: function(data) {
            // This methods is added for compatibility with module https://www.odoo.com/apps/modules/10.0/pos_multi_session/
            /* It is necessary to check the presence of the super method
            in order to be able to inherit the apply_ms_data
            without calling require('pos_multi_session')
            and without adding pos_multi_session in dependencies in the manifest.

            At the time of loading, the super method may not exist. So, if the js file is loaded
            first among all inherited, then there is no super method and it is not called.
            If the file is not the first, then the super method is already created by other modules,
            and we call super method. */
            if (OrderlineSuper.prototype.apply_ms_data) {
                OrderlineSuper.prototype.apply_ms_data.apply(this, arguments);
            }
            if (this.current_state && this.current_state.technical_name !== data.current_state.technical_name && data.current_state.sound_signal) {
                var audio = new Audio(session.url("/pos_multi_session_kitchen/static/src/audio/state.wav"));
                audio.play();
            }

            this.current_state = data.current_state;
            this.states = data.states;
            this.start_timer();
            this.trigger('change', this);
        }
    });
});
