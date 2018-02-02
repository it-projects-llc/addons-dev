odoo.define('pos_multi_session_kitchen.models', function(require){

    var multi_session = require('pos_multi_session');
    var core = require('web.core');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');

    var _t = core._t;

    // load all line states
    models.load_models({
        model: 'pos.order.line.state',
        fields: ['name', 'technical_name', 'type', 'sequence', 'show_in_kitchen'],
        loaded: function(self, states){
            var sorting_states = function(idOne, idTwo){
                return idOne.sequence - idTwo.sequence;
            };
            if (states) {
                self.states = states.sort(sorting_states);
            }
        },
    });

    // load all line buttons
    models.load_models({
        model: 'pos.order.line.button',
        domain: function(self){
            if (self.config.screen === 'kitchen') {
                return [['show_in_kitchen','=',true]];
            } else {
                return [['show_for_waiters','=',true]];
            }
        },
        fields: ['name', 'background_color', 'name_color', 'show_for_waiters', 'show_in_kitchen', 'next_state_id'],
        loaded: function(self, line_buttons){
            self.line_buttons = line_buttons;
        },
    });

    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        ms_on_update: function(message, sync_all) {
            PosModelSuper.prototype.ms_on_update.apply(this, arguments);
            data = message.data || {};
            var order = false;
            if (data.uid) {
                order = this.get('orders').find(function(item){
                    return item.uid === data.uid;
                });
            }
            this.trigger('change:kitchen', order, data.uid);
        },
        get_state_by_id: function(id){
            return this.states.filter(function(state){
                return state.id === id;
            })
        }
    });

    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        initialize: function(){
            var self = this;
            this.states = [];
            OrderlineSuper.prototype.initialize.apply(this, arguments);
            if (!this.states || (this.states && !this.states.length)) {
                this.states = this.pos.states;
                this.set_state(this.pos.states[0]);
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
            var index = this.states.indexOf(state);
            if (index !== -1) {
                var active_state = this.states.find(function(current_state){
                    return state.id === current_state.id;
                });

                if (active_state) {
                    active_state.active = true;
                }
                this.current_state = active_state;
            }
            this.trigger('change', this);
            this.order.trigger('change:sync');
        },
        apply_ms_data: function(data) {
            // This methods is added for compatibility with module https://www.odoo.com/apps/modules/10.0/pos_multi_session/
            /*
            It is necessary to check the presence of the super method
            in order to be able to inherit the apply_ms_data
            without calling require('pos_multi_session')
            and without adding pos_multi_session in dependencies in the manifest.

            At the time of loading, the super method may not exist. So, if the js file is loaded
            first among all inherited, then there is no super method and it is not called.
            If the file is not the first, then the super method is already created by other modules,
            and we call super method.
            */
            if (OrderlineSuper.prototype.apply_ms_data) {
                OrderlineSuper.prototype.apply_ms_data.apply(this, arguments);
            }
            this.current_state = data.current_state;
            this.states = data.states;
            this.trigger('change', this);
        },
        get_button_by_id: function(id) {
            return this.pos.line_buttons.find(function(button){
                return button.id === id;
            });
        },
    });
});
