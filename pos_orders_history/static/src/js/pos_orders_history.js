odoo.define('pos_orders_history', function (require) {
    "use strict";
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.gui');
    var PosDB = require('point_of_sale.DB');
    var core = require('web.core');
    var QWeb = core.qweb;
    var Model = require('web.Model');

    var OrdersHistoryButton = screens.OrdersHistoryButton = {};
    var OrdersHistoryScreenWidget = screens.OrdersHistoryScreenWidget = {};
    var OrderLinesHistoryScreenWidget = screens.OrderLinesHistoryScreenWidget = {};

    var _super_pos_model = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        _flush_orders: function(orders, options) {
            var res =  _super_pos_model._flush_orders.call(this, orders, options);
            var self = this;
            res.then(function(result) {
                if (result && result.length) {
                    result.forEach(function(id) {
                        self.get_order_history(id);
                        self.get_order_history_lines(id);
                    });
                }
            });
            return res;
        },
        get_order_history: function (id) {
            var self = this;
            new Model('pos.order').call('search_read', [[['id', '=', id]]]).done(function(order) {
                console.log("new order", order);
                var orders = self.db.pos_orders_history.concat(order);
                self.db.pos_orders_history = orders;
                self.db.sorted_orders_history(orders);
            });
        },
        get_order_history_lines: function (id) {
            var self = this;
            new Model('pos.order.line').call('search_read', [[['order_id', '=', id]]]).done(function(lines) {
                lines.forEach(function(line){
                    self.db.line_by_id[line.id] = line;
                });
//                self.db.pos_orders_history_lines = self.db.pos_orders_history_lines.concat(lines);

//                self.pos.db.add_order_history(order);
//                  read orderline by id
            });
        },
    });
    models.load_models({
        model: 'pos.order',
        fields: ['id', 'name', 'pos_reference', 'partner_id', 'date_order', 'user_id', 'amount_total', 'lines', 'state', 'sale_journal'],
        loaded: function(self, orders) {
            self.db.pos_orders_history = orders;
            self.db.orders_history_by_id = {};
            self.db.sorted_orders_history(orders);
            orders.forEach(function(order){
                self.db.orders_history_by_id[order.id] = order;
                self.db.order_search_string += self.db._order_search_string(order);
            });
        },
    });

    models.load_models({
        model: 'pos.order.line',
        fields: ['product_id', 'qty', 'price_unit', 'discount','tax_ids','price_subtotal', 'price_subtotal_incl'],
        loaded: function(self, lines) {
            self.db.pos_orders_history_lines = lines;
            self.db.line_by_id = {};
            lines.forEach(function(line){
                self.db.line_by_id[line.id] = line;
            });
        },
    });

    PosDB.include({
        init: function(options){
            this.order_search_string = "";
            this.sorted_orders = [];
            this._super.apply(this, arguments);
        },
        search_order: function(query){
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(' ','.+');
                var re = RegExp("([0-9]+):.*?"+query,"gi");
            }catch(e){
                return [];
            }
            var results = [];
            for(var i = 0; i < this.limit; i++){
                var r = re.exec(this.order_search_string);
                if(r) {
                    var id = Number(r[1]);
                    var exist_order = this.orders_history_by_id[id];
                    if (exist_order) {
                        results.push(exist_order);
                    }
                }else{
                    break;
                }
            }
            return results;
        },
        _order_search_string: function(order){
            var str = order.name;
            if(order.pos_reference){
                str += '|' + order.pos_reference;
            }
            if(order.partner_id){
                str += '|' + order.partner_id[1];
            }
            if(order.date_order){
                str += '|' + order.date_order;
            }
            if(order.user_id){
                str += '|' + order.user_id[1];
            }
            if(order.amount_total){
                str += '|' + order.amount_total;
            }
            if(order.state){
                str += '|' + order.state;
            }
            str = String(order.id) + ':' + str.replace(':','') + '\n';
            return str;
        },
        get_sorted_orders_history: function(count) {
            return this.sorted_orders.slice(0, count);
        },
        sorted_orders_history: function(orders) {
           var orders_history = orders;
            function compareNumeric(order1, order2) {
                return order2.id - order1.id;
            }
            this.sorted_orders = orders_history.sort(compareNumeric);
        },
    });

    OrdersHistoryButton = screens.ActionButtonWidget.extend({
        template: 'OrdersHistoryButton',
        button_click: function(){
            if (this.pos.db.pos_orders_history.length) {
                this.gui.show_screen('orders_history_screen');
            }
        },
    });

    screens.define_action_button({
        'name': 'orders_history_button',
        'widget': OrdersHistoryButton,
        'condition': function(){
            return this.pos.config.orders_history;
        },
    });

    OrdersHistoryScreenWidget = screens.ScreenWidget.extend({
        template: 'OrdersHistoryScreenWidget',

        init: function(parent, options){
            this._super(parent, options);
            this.orders_history_cache = new screens.DomCache();
        },
        auto_back: true,

        show: function(){
            var self = this;
            this._super();
            this.$('.back').click(function(){
                self.gui.show_screen('products');
            });

            var orders = this.pos.db.get_sorted_orders_history(1000);

            this.render_list(orders);
            this.$('.details').click(function(event){
                var order = self.pos.db.orders_history_by_id[Number(this.dataset.id)];
                self.gui.show_screen('order_lines_history_screen', {order: order});
            });
            var search_timeout = null;
            if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
                this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }
            this.$('.searchbox input').on('keypress',function(event){
                clearTimeout(search_timeout);

                var query = this.value;

                search_timeout = setTimeout(function(){
                    self.perform_search(query,event.which === 13);
                },70);
            });

            this.$('.searchbox .search-clear').click(function(){
                self.clear_search();
            });
        },
        render_list: function(orders) {
            var contents = this.$el[0].querySelector('.order-list-contents');
            contents.innerHTML = "";

            for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
                var order = orders[i];
                var orderline = this.orders_history_cache.get_node(order.id);
                if(!orderline){
                    var orderline_html = QWeb.render('OrderHistory',{widget: this, order:orders[i]});
                    orderline = document.createElement('tbody');
                    orderline.innerHTML = orderline_html;
                    orderline = orderline.childNodes[1];
                    this.orders_history_cache.cache_node(order.id, orderline);
                }
                contents.appendChild(orderline);
            }
        },
        clear_search: function(){
            var orders = this.pos.db.pos_orders_history;
            this.render_list(orders);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },
        perform_search: function(query, associate_result){
            var orders = false;
            if(query){
                orders = this.pos.db.search_order(query);
                this.render_list(orders);
            }else{
                orders = this.pos.db.pos_orders_history;
                this.render_list(orders);
            }
        },
    });
    gui.define_screen({name:'orders_history_screen', widget: OrdersHistoryScreenWidget});

    OrderLinesHistoryScreenWidget = screens.ScreenWidget.extend({
        template: 'OrderLinesHistoryScreenWidget',

        init: function(parent, options){
            this._super(parent, options);
            this.lines_history_cache = new screens.DomCache();
            this.order_history_details_cache = new screens.DomCache();
        },
        auto_back: true,

        show: function(options){
            console.log("show options", options);
            var self = this;
            this._super();
            this.$('.back').click(function(){
                self.gui.show_screen('orders_history_screen');
            });
            this.order = this.get_order();
            var lines = [];
            this.order.lines.forEach(function(line_id) {
                var orderline = self.pos.db.line_by_id[line_id];
                orderline.image = self.get_product_image_url(orderline.product_id[0]);
                lines.push(self.pos.db.line_by_id[line_id]);
            });
            this.render_list(lines);
            this.render_order_details(this.order);
        },
        render_list: function(lines) {
            var contents = this.$el[0].querySelector('.orderline-list-contents');
            contents.innerHTML = "";

            for(var i = 0, len = Math.min(lines.length,1000); i < len; i++){
                var line = lines[i];
                var orderline = this.lines_history_cache.get_node(line.id);
                if(!orderline){
                    var orderline_html = QWeb.render('LineHistory',{widget: this, line:lines[i]});
                    orderline = document.createElement('tbody');
                    orderline.innerHTML = orderline_html;
                    orderline = orderline.childNodes[1];
                    this.lines_history_cache.cache_node(line.id, orderline);
                }
                contents.appendChild(orderline);
            }
        },
        render_order_details: function(order) {
            var contents = this.$el[0].querySelector('.order-details-content');
            contents.innerHTML = "";
            var order_content = this.order_history_details_cache.get_node(order.id);
            if (!order_content) {
                var order_html = QWeb.render('OrderHistoryDetails',{order:order});
                order_content = document.createElement('div');
                order_content.innerHTML = order_html;
                order_content = order_content.childNodes[1];
                this.order_history_details_cache.cache_node(order.id, order_content);
            }
            contents.appendChild(order_content);
        },
        get_order: function(){
            return this.gui.get_current_screen_param('order');
        },
        get_product_image_url: function(product_id){
            return window.location.origin + '/web/image?model=product.product&field=image_small&id='+product_id;
        },
    });
    gui.define_screen({name:'order_lines_history_screen', widget: OrderLinesHistoryScreenWidget});

    return screens;
});
