odoo.define('pos_multi_session_kitchen.screens', function(require){

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var pyeval = require('web.pyeval');

    var QWeb = core.qweb;
    var _t = core._t;

    /*--------------------------------------*\
     |         THE KITCHEN SCREEN           |
    \*======================================*/

    // The Kitchen Screen display orders in the kitchen

    var KitchenScreenWidget = screens.ScreenWidget.extend({
        template: "KitchenScreenWidget",
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
            this.order = this.get_orders();
            this.pos.on('change:kitchen', function(order, uid){
                self.rerender_order(order, uid);
            });
        },
        show: function(){
            var self = this;
            this._super();
            if (this.pos.config.show_floors_plan) {
                // get orders by current table
                var order = this.get_orders().filter(function(current_order){
                    return current_order.table.id === self.pos.table.id;
                });
                this.render_list(order);
                this.render_floor_button();
            }
        },
        orderline_filtering: function(lines) {
            var filtered_lines = this.filter_on_states(this.filter_on_category(lines));
            return filtered_lines;
        },
        filter_on_states: function(lines) {
            // filter lines on kitchen states
            return lines.filter(function(line){
                return line.current_state.show_in_kitchen;
            });
        },
        filter_on_category: function(lines) {
            var kitchen_category_ids = this.pos.config.cat_ids;
            return lines.filter(function(line){
                return jQuery.inArray(line.product.pos_categ_id[0], kitchen_category_ids) !== -1;
            });
        },
        // TODO: filter lines on kitchen
//        filter_on_kitchen: function(lines){
//            return lines;
//        },
        rerender_order: function(order, uid) {
            if (!order) {
                // if the order does not exist, remove the order from the kitchen screen
                this.remove_order(uid);
                return false;
            }
            var lines = this.orderline_filtering(order.get_orderlines());
            var content = this.$el.find('.order-block[data-uid="'+ uid +'"]');
            if (content.length) {
                // if the order is exist in kitchen screen, update the order
                this.update_order(order, lines);
            } else {
                this.render_list();
            }
            if (this.pos.table && this.pos.table.floor) {
                this.render_floor_button();
            }
        },
        render_list: function(orders_collection){
            var self = this;
            var orders = orders_collection || this.get_orders();

            var sort_priority = function(idOne, idTwo) {
                return idTwo.priority - idOne.priority;
            };
            orders = orders.sort(sort_priority);

            var contents = this.$el[0].querySelector('.order-list-contents');
            contents.innerHTML = "";
            for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
                var order = orders[i];
                var lines = self.orderline_filtering(order.get_orderlines());
                this.append_order(order, lines);
            }
        },
        floor_button_click_handler: function(){
            this.pos.table = null;
            this.gui.show_screen('floors');
            this.chrome.$el.removeClass('kitchen');
        },
        render_floor_button: function() {
            var self = this;
            if (this.pos.config.show_floors_plan && this.pos.table && this.pos.table.floor) {
                var content = this.getParent().$('.orders, .floor-button');
                content.replaceWith(QWeb.render('BackToFloorButton',{table: this.pos.table, floor:this.pos.table.floor}));
                this.getParent().$('.order-selector').removeClass('oe_invisible');
                this.getParent().$('.floor-button').click(function(){
                    self.floor_button_click_handler();
                });
            }
        },
        append_order: function(order, lines) {
            var contents = this.$el[0].querySelector('.order-list-contents');
            if (lines && lines.length) {
                var order_html = QWeb.render('KitchenOrder',{widget: this, order:order});
                var order_el = document.createElement('div');
                order_el.innerHTML = order_html;
                order_el = order_el.childNodes[1];
                contents.appendChild(order_el);
                this.render_lines(order, lines);
            }
        },
        remove_order: function(uid) {
            var order = this.$el.find('.order-block[data-uid="'+ uid +'"]');
            order.remove();
        },
        update_order: function(order, lines) {
            if (!lines.length) {
                this.remove_order(order.uid);
                return false;
            }
            var content = this.$el.find('.order-block[data-uid="'+ order.uid +'"]');
            if (order.priority !== content.data('priority')) {
                this.render_list();
                return;
            }
            var order_html = QWeb.render('KitchenOrder',{widget: this, order:order});
            content.replaceWith(order_html);
            this.render_lines(order, lines);
        },
        get_product_image_url: function(product){
            return window.location.origin + '/web/image?model=product.product&field=image_small&id='+product.id;
        },
        renderElement: function() {
            this._super();
            this.render_list();
        },
        render_lines: function(order, lines) {
            // get lines of current order
            var self = this;
            var contents = this.$el[0].querySelector('.order-block[data-uid="'+order.uid+'"] .order-line-list-contents');
            contents.innerHTML = "";

            for(var i = 0, len = Math.min(lines.length,1000); i < len; i++){
                var line = lines[i];
                this.check_line_buttons(line);
                var product = line.product;
                var orderline_html = QWeb.render('KitchenOrderLine',{
                    widget: this,
                    line:line,
                    image_url: this.get_product_image_url(line.product),
                });
                var orderline = document.createElement('tbody');
                orderline.innerHTML = orderline_html;
                orderline = orderline.childNodes[1];
                $(orderline).find('.line-button').click(function(event){
                    self.click_line_button(event, $(this));
                });
                line.kitchen_timer = $(orderline).find('.state_timer .time');
                contents.appendChild(orderline);
            }
        },
        check_line_buttons: function(line) {
            var self = this;
            // optional arguments for custom function
            var state = line.current_state.name;
            var product = line.product;
            var quantity = line.get_quantity();
            var price = line.price;

            // run the condition code for each button
            line.line_buttons.forEach(function(button){
                var code = button.condition_code;
                if (code) {
                    button.hide = pyeval.py_eval(code, {state:state, product:product, quantity:quantity, price: price});
                }
            });
        },
        click_line_button: function(event, element) {
            var order = this.get_order_by_uid(element.parents('.order-block').data('uid'));
            var line = order.get_orderlines().find(function(current_line){
                return current_line.uid === element.parents('.line').data('uid');
            });
            var button = this.pos.get_kitchen_button_by_id(element.data('id'));
            var state = this.pos.get_state_by_id(button.next_state_id[0]);

            // set next state for line
            if (state) {
                line.set_state(state);
            }

            if (button.action_close) {
                line.action_close();
            }

            // update order
            this.rerender_order(order, order.uid);
        },
        get_orders: function() {
            return this.pos.get('orders').models;
        },
        get_orderline_by_uid: function(uid) {
            var order = this.pos.get_order();
            var orderline = null;
            if (order) {
                orderline = order.get_orderlines().find(function(line){
                    return line.uid === uid;
                });
            }
            return orderline;
        },
        get_order_by_uid: function(uid){
            return this.get_orders().find(function(order){
                return order.uid === uid;
            });
        }
    });

    gui.define_screen({
        'name': 'kitchen',
        'widget': KitchenScreenWidget,
        'condition': function(){
            return this.pos.config.screen === 'kitchen';
        },
    });

    screens.OrderWidget.include({
        change_selected_order: function() {
            this._super();
            var order = this.pos.get_order();
            if (order && order.get_selected_orderline()) {
                this.check_qty_numpad_of_line(order.get_selected_orderline());
            } else {
                $('.numpad').find("[data-mode='quantity']").removeClass('disable');
                $(".pads .number-char").removeClass('disable');
            }
        },
        orderline_remove: function(line){
            line.stop_timer();
            this._super(line);
        },
        check_line_buttons: function(line) {
            var self = this;
            if (!line.line_buttons || !line.current_state) {
                return;
            }
            // optional arguments for custom function
            var state = line.current_state.name;
            var product = line.product;
            var quantity = line.get_quantity();
            var price = line.price;

            // run the condition code for each button
            line.line_buttons.forEach(function(button){
                var code = button.condition_code;
                if (code) {
                    button.hide = pyeval.py_eval(code, {state:state, product:product, quantity:quantity, price: price});
                }
            });
        },
        orderline_change: function(line) {
            this.check_qty_numpad_of_line(line);
            this._super(line);
        },
        check_qty_numpad_of_line: function(line) {
            var state = this.getParent().numpad.state;
            var mode = state.get('mode');
            if (mode === 'quantity' && line.get_active_states().length > 1) {
                $('.numpad').find("[data-mode='quantity']").addClass('disable');
                $(".pads .number-char").addClass('disable');
            } else {
                $('.numpad').find("[data-mode='quantity']").removeClass('disable');
                $(".pads .number-char").removeClass('disable');
            }
        },
        render_orderline: function(orderline){
            var self = this;
            this.check_line_buttons(orderline);
            var el = this._super(orderline);
            $(el).find('.line-button').click(function(event) {
                self.click_line_buttons(orderline, $(this));
            });
            orderline.waiters_timer = $(el).find(".state_timer .time");
            return el;
        },
        click_line_buttons: function(orderline, element){
            var button = this.pos.get_kitchen_button_by_id(element.data('id'));
            var state = this.pos.get_state_by_id(button.next_state_id[0]);

            // set next state for orderline
            if (state) {
                orderline.set_state(state);
            }

            if (button.action_close) {
                orderline.action_close();
            }
        },
        update_summary: function(){
            this._super();
            // TODO: show or hide order buttons
        },
    });

    screens.NumpadWidget.include({
        clickDeleteLastChar: function() {
            var self = this;
            var mode = this.state.get('mode');
            var order = this.pos.get_order();
            var current_line = order.get_selected_orderline();
            if (mode === 'quantity' && current_line.get_active_states().length > 1) {
                if (current_line.quantity === 0) {
                    current_line.set_quantity('remove');
                    return false;
                }
                this.gui.show_popup('number', {
                    'title': _t('Quantity for Cancellation'),
                    'value': 1,
                    'confirm': function(value) {
                        current_line.set_quantity(current_line.quantity - value);
                    }
                });
            } else {
                return this._super();
            }
        },
        changedMode: function() {
            var mode = this.state.get('mode');
            var order = this.pos.get_order();
            if (order) {
                var line = order.get_selected_orderline();
                if (line) {
                    if (mode === 'quantity' && line.get_active_states().length > 1) {
                        $('.numpad').find("[data-mode='quantity']").addClass('disable');
                        $(".pads .number-char").addClass('disable');
                    } else {
                        $('.numpad').find("[data-mode='quantity']").removeClass('disable');
                        $(".pads .number-char").removeClass('disable');
                    }
                }
            }
            this._super();
        }
    });

    var OrderCustomButtons = screens.ActionButtonWidget.extend({
        template: 'OrderCustomButtons',
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
            this.buttons = [];
            this.pos.config.custom_button_ids.forEach(function(id) {
                self.buttons.push(self.pos.get_order_buttons_by_id(id));
            });
        },
        renderElement: function(){
            var self = this;
            this._super();
            this.$el.click(function(event){
                self.custom_button_click($(this));
            });
        },
        custom_button_click: function(el) {
            var order = this.pos.get_order();
            var button = this.buttons.find(function(current_button) {
                return current_button.id === el.data('id');
            });

            if (button.remove_tag_id) {
                var remove_tag = this.pos.get_order_tags_by_id(button.remove_tag_id[0]);
                order.remove_tag(remove_tag);
            }

            if (button.next_tag_id) {
                var new_tag = this.pos.get_order_tags_by_id(button.next_tag_id[0]);
                order.set_tag(new_tag);
            }
        },
        get_custom_buttons: function() {
            return this.buttons;
        },
    });

    screens.define_action_button({
        'name': 'custom_buttons',
        'widget': OrderCustomButtons,
        'condition': function(){
            return this.pos.config.screen === 'waiter';
        },
    });

    screens.KitchenScreenWidget = KitchenScreenWidget;
    return screens;
});
