odoo.define('pos_multi_session_kitchen.screens', function(require){

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');

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
            this.pos.on('change:kitchen', function(order, uid){
                self.rerender_order(order, uid);
            });
        },
        orderline_filtering: function(lines) {
            return this.filter_on_stages(this.filter_on_category(lines));
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
        rerender_order: function(order, uid) {
            if (!order) {
                // if the order does not exist, remove the order from the kitchen screen
                this.remove_order(uid);
                return false;
            }
            var lines = this.orderline_filtering(order.get_orderlines());
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
            var contents = this.$el[0].querySelector('.order-list-contents');
            contents.innerHTML = "";
            for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
                var order = orders[i];
                var lines = self.orderline_filtering(order.get_orderlines());
                this.append_order(order, lines);
            }
        },
        append_order: function(order, lines) {
            var contents = this.$el[0].querySelector('.order-list-contents');
            if (lines && lines.length) {
                var order_html = QWeb.render('KitchenOrder',{widget: this, order:order});
                var order_el = document.createElement('tbody');
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
            var self = this;
            this._super();
            this.orders = this.pos.get('orders').models;
            this.render_list(this.orders);
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
            return this.orders.find(function(order){
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

    screens.KitchenScreenWidget = KitchenScreenWidget;
    return screens;
});
