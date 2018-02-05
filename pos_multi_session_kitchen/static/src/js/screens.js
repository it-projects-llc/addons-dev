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
                var order = this.get_orders().filter(function(order){
                    return order.table.id === self.pos.table.id;
                });
                this.render_list(order);
                this.render_floor_button();
            }
        },
        orderline_filtering: function(lines) {
            var filtered_lines = this.filter_on_stages(this.filter_on_category(lines));
            return filtered_lines;
        },
        filter_on_stages: function(lines) {
            // filter lines on kitchen stages
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
        filter_on_kitchen: function(lines){
            return lines;
        },
        rerender_order: function(order, uid) {
            if (!order) {
                // if the order does not exist, remove the order from the kitchen screen
                this.remove_order(uid);
                return false;
            }
//            var lines = this.orderline_filtering(order.get_orderlines());
            var lines = order.get_orderlines();
            var content = this.$el.find('.order[data-uid="'+ uid +'"]');
            if (content.length) {
                // if the order is exist in kitchen screen, update the order
                this.update_order(order, lines);
            } else {
                this.append_order(order, lines);
            }
        },
        render_list: function(orders){
            var self = this;
            var orders = orders || this.get_orders();
            var contents = this.$el[0].querySelector('.order-list-contents');
            contents.innerHTML = "";
            for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
                var order = orders[i];
                var lines = order.get_orderlines();
//                var lines = self.orderline_filtering(order.get_orderlines());
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
            var order = this.$el.find('.order[data-uid="'+ uid +'"]');
            order.remove();
        },
        update_order: function(order, lines) {
            var content = this.$el.find('.order[data-uid="'+ order.uid +'"]');
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
            this.render_floor_button();
        },
        render_lines: function(order, lines) {
            // get lines of current order
            var self = this;
            var contents = this.$el[0].querySelector('.order[data-uid="'+order.uid+'"] .order-line-list-contents');
            contents.innerHTML = "";

            for(var i = 0, len = Math.min(lines.length,1000); i < len; i++){
                var line = lines[i];
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
                contents.appendChild(orderline);
            }
        },
        click_line_button: function(event, element) {
            var order = this.get_order_by_uid(element.parents('.order').data('uid'));
            var line = order.get_orderlines().find(function(line){
                return line.uid === element.parents('.line').data('uid');
            });
            var button = line.get_button_by_id(element.data('id'));
            console.log(order, line, button);
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
        orderline_change: function(line){
            this.check_line_buttons(line);
            this._super(line);
        },
        check_line_buttons: function(line) {
            var self = this;
            // optional arguments for custom function
            var state = line.current_state;
            var product = line.product;
            var quantity = line.get_quantity();
            var price = line.price;

            // run the condition code for each button
            // TODO: don't use the eval function
            line.kitchen_buttons.forEach(function(button){
                var code = button.condition_code;
                if (code) {
                    eval(code);
                }
            });
        },
        render_orderline: function(orderline){
            var self = this;
            var el = this._super(orderline);
            $(el).find('.line-button').click(function(event) {
                self.click_line_buttons(orderline, $(this));
            });
            return el;
        },
        click_line_buttons: function(orderline, element){
            var button = this.pos.get_kitchen_button_by_id(element.data('id'));
            var state = this.pos.get_state_by_id(button.next_state_id[0]);

            // set next state for orderline
            if (state) {
                orderline.set_state(state);
            }
        }
    });

    screens.KitchenScreenWidget = KitchenScreenWidget;
    return screens;
});
