odoo.define('pos_pricelist_discount.models', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
	var models = require('pos_pricelist.models');
	var core = require('web.core');
	var utils = require('web.utils');
	var formats = require('web.formats');
	var gui = require('point_of_sale.gui');
	var PopupWidget = require('point_of_sale.popups');
	var devices = require('point_of_sale.devices');

	var QWeb = core.qweb;
	var _t = core._t;
    var round_di = utils.round_decimals;


    devices.BarcodeReader.include({
        scan: function(code){
            if (!code) {
                return;
            }
            var parsed_result = this.barcode_parser.parse_barcode(code);
            if (this.pos.opened_promo_popup) {
                this.pos.gui.current_popup.perform_search(parsed_result.base_code, true);
                this.pos.gui.current_popup.$('.searchbox input').val(parsed_result.base_code);
                this.pos.gui.current_popup.search_value = false;
            } else {
                this._super(code);
            }
        },
    });

    var PromoCategoryPopupWidget = PopupWidget.extend({
        template: 'PromoCategoryPopupWidget',
        events: _.extend({}, PopupWidget.prototype.events, {
            'click .promo-button.button.promo-home':  function() {
                this.category = false;
                this.search_value = false;
                this.current_screen = 'categories';
                this.renderPromoPopup();
            },
        }),
        init: function(parent, options) {
            this._super(parent, options);
            this.limit = 100;
            var self = this;
            this.product_search_string = "";
            this.category = false;
            this.current_screen = 'categories';
            this.click_product_handler = function(){
                var product = self.pos.db.get_product_by_id(this.dataset.productId);
                self.category = false;
                self.current_screen = 'categories';
                var order = self.pos.get_order();
                self.pos.opened_promo_popup = false;
                self.click_confirm();
                if (self.order_promo) {
                    order.add_promo_product(product, self.rule_id, self.quantity, product.pos_category_ids, self.min_quantity)
                } else {
                    var current_productline = order.get_selected_orderline();
                    current_productline.add_promo_product(product, self.rule_id, self.quantity, this.quantity_included, self.min_quantity)
                    order.promo_categories.push({rule_id: self.rule_id, product: product});
                }
            };
            this.click_category_handler = function() {
                self.set_active_promo_category(self.pos.db.get_category_by_id(Number(this.dataset.categoryId)));
                self.current_screen = 'products';
                self.renderPromoPopup();
            };
            this.promo_product_cache = new screens.DomCache();
            this.promo_category_cache = new screens.DomCache();
        },
        show: function(options){
            var self = this;
            options = options || {};
            this.rule_id = options.rule_id;
            this.quantity = options.quantity;
            this.quantity_included = options.quantity_included;
            this.category_ids = options.category_ids;
            this.order_promo = options.order_promo || false;
            this.min_quantity = options.min_quantity || false;
            this.pos.opened_promo_popup = true;
            if (!this.category_ids) {
                return false;
            }
            this.promo_categories = [];
            this.category_ids.forEach(function(id) {
                self.promo_categories.push(self.pos.db.get_category_by_id(id));
            });
            this.promo_categories[0].active = true;
            this._super(options);
            this.renderPromoPopup();
        },
        get_product_image_url: function(product){
            return window.location.origin + '/web/image?model=product.product&field=image_small&id='+product.id;
        },
        get_category_image_url: function(category){
            return window.location.origin + '/web/image?model=pos.category&field=image_medium&id='+category.id;
        },
        render_product: function(product){
            var cached = this.promo_product_cache.get_node(product.id);
            if(!cached) {
                var image_url = this.get_product_image_url(product);
                var product_html = QWeb.render('Product',{
                        widget:  this,
                        product: product,
                        image_url: this.get_product_image_url(product),
                    });
                var product_node = document.createElement('div');
                product_node.innerHTML = product_html;
                product_node = product_node.childNodes[1];
                this.promo_product_cache.cache_node(product.id,product_node);
                return product_node;
            }
            return cached;
        },
        render_search_box: function() {
            var contents = this.$el[0].querySelector('.promo-search-box');
            contents.innerHTML = "";
            var searchbox_html = QWeb.render('PromoSearchBox');
            var box = document.createElement('div');
            box.innerHTML = searchbox_html;
            contents.appendChild(box);
        },
        render_category: function(category, with_image){
            var cached = this.promo_category_cache.get_node(category.id);
            if(!cached){
                if(with_image){
                    var image_url = this.get_category_image_url(category);
                    var category_html = QWeb.render('CategoryButton',{
                            widget:  this,
                            category: category,
                            image_url: this.get_category_image_url(category),
                        });
                        category_html = _.str.trim(category_html);
                    var category_node = document.createElement('div');
                        category_node.innerHTML = category_html;
                        category_node = category_node.childNodes[0];
                } else{
                    var category_html = QWeb.render('CategorySimpleButton',{
                            widget:  this,
                            category: category,
                        });
                        category_html = _.str.trim(category_html);
                    var category_node = document.createElement('div');
                        category_node.innerHTML = category_html;
                        category_node = category_node.childNodes[0];
                }
                this.promo_category_cache.cache_node(category.id,category_node);
                return category_node;
            }
            return cached;
        },
        renderPromoPopup: function(new_products) {
            var self = this;
            if (!this.search_value) {
                this.renderElement();
            }
            if (!this.category) {
                var categories = this.promo_categories;
                var products = [];
                categories.forEach(function(category) {
                    var current_products = self.pos.db.get_product_by_category(category.id);
                    products = products.concat(current_products);
                });
                this.product_search_string = "";
                products.forEach(function(product){
                    self.product_search_string += self._product_search_string(product);
                });
                var list_categories_container = this.el.querySelector('.promo-category-list');
                var withpics = this.pos.config.iface_display_categ_images;
                categories.forEach(function(category) {
                    var category_node = self.render_category(category, withpics);
                    category_node.addEventListener('click', self.click_category_handler);
                    list_categories_container.appendChild(category_node);
                });
                var buttons = this.el.querySelectorAll('.js-category-switch');
                buttons.forEach(function(button){
                    button.addEventListener('click', self.click_category_handler);
                });
            } else {
                var products = this.pos.db.get_product_by_category(this.category.id);
                if (!this.used_barcode_scanning) {
                    this.product_search_string = "";
                    products.forEach(function(product){
                        self.product_search_string += self._product_search_string(product);
                    });
                }
                if (new_products) {
                    products = new_products;
                }
                if (this.search_value) {
                    this.$('.promo-product-list').empty();
                }
                var list_product_container = this.el.querySelector('.promo-product-list');
                products.forEach(function(product){
                    var product_node = self.render_product(product);
                    product_node.addEventListener('click', self.click_product_handler);
                    list_product_container.appendChild(product_node);
                });
                if (this.used_barcode_scanning || !this.search_value) {
                    this.render_search_box();
                    this.add_search_events();
                    this.used_barcode_scanning = false;
                }
            }
        },
        add_search_events: function() {
            var self = this;
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
        clear_search: function(){
            this.search_value = false;
            this.renderPromoPopup();
        },
        set_active_promo_category: function(category) {
            this.category = category;
        },
        perform_search: function(query, associate_result){
            var products = false;
            if(query){
                this.search_value = true;
                products = this.search_product(query);
                if (products && this.current_screen == 'categories') {
                    this.current_screen = 'products';
                    // show only one product after scanning barcode
                    this.search_value = false;
                    this.used_barcode_scanning = true;
                    this.set_active_promo_category(this.pos.db.get_category_by_id(products[0].pos_category_ids[0]));
                };
                this.renderPromoPopup(products);
            } else {
                this.search_value = true;
                this.renderPromoPopup();
            }
        },
        search_product: function(query){
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(' ','.+');
                var re = RegExp("([0-9]+):.*?"+query,"gi");
            }catch(e){
                return [];
            }
            var results = [];
            for(var i = 0; i < this.limit; i++){
                var r = re.exec(this.product_search_string);
                if(r) {
                    var id = Number(r[1]);
                    var exist_product = this.pos.db.get_product_by_id(id);
                    if (exist_product) {
                        results.push(exist_product);
                    }
                }else{
                    break;
                }
            }
            return results;
        },
        _product_search_string: function(product){
            var str = product.display_name;

            if(product.barcode){
                str += '|' + product.barcode;
            }
            if(product.default_code){
                str += '|' + product.default_code;
            }
            str = String(product.id) + ':' + str.replace(':','') + '\n';
            return str;
        },
    });
    gui.define_popup({name:'promo_category', widget: PromoCategoryPopupWidget});
    screens.ReceiptScreenWidget.include({
        render_receipt: function() {
            var order = this.pos.get_order();
            var lines = order.get_orderlines();
            var lines_without_discount = order.get_all_orderlines_without_discount();
            if (lines_without_discount && lines.length > lines_without_discount.length) {
                this.discount_product = order.get_discount_orderline();
                this.subtotal = order.get_total_without_tax() - this.discount_product.price;
                this.discount = order.get_total_discount() + (- this.discount_product.price);
                this.$('.pos-receipt-container').html(QWeb.render('PosTicket',{
                    widget:this,
                    order: order,
                    receipt: order.export_for_printing(),
                    orderlines: order.get_all_orderlines_without_discount(),
                    paymentlines: order.get_paymentlines(),
                }));
            } else {
                this._super();
            }
        }
    });
    screens.OrderWidget.include({
        render_orderline: function(orderline){
            var el_str  = QWeb.render('Orderline',{widget:this, line:orderline});
            var el_node = document.createElement('div');
            el_node.innerHTML = _.str.trim(el_str);
            el_node = el_node.childNodes[0];
            if (el_node) {
                return this._super(orderline);
            }
        },
        renderElement: function(scrollbottom){
            var order  = this.pos.get_order();
            if (!order) {
                return;
            }
            var orderlines = order.get_orderlines();
            var el_str  = QWeb.render('OrderWidget',{widget:this, order:order, orderlines:orderlines});
            var el_node = document.createElement('div');
                el_node.innerHTML = _.str.trim(el_str);
                el_node = el_node.childNodes[0];
            var list_container = el_node.querySelector('.orderlines');
            var line = order.get_discount_orderline();
            if (!line) {
                this._super(scrollbottom);
            } else {
                orderlines = order.get_all_orderlines_without_discount();
                for(var i = 0, len = orderlines.length; i < len; i++) {
                    var orderline = this.render_orderline(orderlines[i]);
                    list_container.appendChild(orderline);
                }
                var discount_line = this.render_orderline(line);
                list_container.appendChild(discount_line);
                if(this.el && this.el.parentNode){
                    this.el.parentNode.replaceChild(el_node,this.el);
                }
                this.el = el_node;
                this.update_summary();
                if(scrollbottom){
                    this.el.querySelector('.order-scroller').scrollTop = 100 * orderlines.length;
                }
            }
        },
        update_summary: function(){
            if (this.el.querySelector('.summary .total .subentry .value')) {
                this._super();
                var order = this.pos.get_order();
                if (order.is_empty()) {
                    return;
                }
                var taxes     = order ? order.get_total_tax() : 0;
                this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(taxes);
            }
        },
        set_value: function(val) {
            var order = this.pos.get_order();
            order.compute_new_discount_price = true;
            if (order.get_selected_orderline() && !order.base_product_id && val !== 'remove') {
                order.get_selected_orderline().old_qty = Number(val) || 0;
                order.get_selected_orderline().change_qty = true;
            }
            if (order.get_selected_orderline() && (!order.get_selected_orderline().promo && !order.get_selected_orderline().discount_product)) {
                this._super(val);
            }
        },
        orderline_add: function(){
            var order = this.pos.get_order();
            if (order && !order.get_last_orderline().promo) {
                this._super();
            } else {
                this.renderElement('and_scroll_to_bottom');
            }
        },
        rerender_orderline: function(order_line){
            if (order_line.node && order_line.node.parentNode) {
                this._super(order_line);
            }
        },
        orderline_remove: function(line){
            if (!line.promo) {
                this._super(line);
            } else {
                this.remove_orderline(line);
                this.update_summary();
            }
        },
        remove_orderline: function(order_line){
            if (this.pos.get_order().get_orderlines().length === 0) {
                this._super(order_line);
            }else if (order_line && order_line.node) {
                this._super(order_line);
            }
        },
    });
    models.load_models({
        model: 'product.pricelist.item',
        fields: [
            'promotional_type',
            'promotional_product_id',
            'promotional_pos_category_ids',
            'promotional_product_quantity',
            'cumulative_quantity',
            'quantity_included',
            'base_type',
            'promotional_product_tmpl_id',
            'base_pos_category_ids',
            'amount_order_total',
            'total_discount_product',
            'base',
            'base_pricelist_id',
            'pricelist_id',
            'categ_id',
            'min_quantity',
            'applied_on',
            'fixed_price',
            'percent_price',
            'price_discount',
            'price_max_margin',
            'price_min_margin',
            'price_round',
            'price_surcharge',
            'product_id',
            'product_tmpl_id',
            'sequence',
            'date_start',
            'date_end'
        ],
        loaded: function(self, items){
            self.db.add_pricelist_items(items);
        },
    });
    var _super_pricelistengine = models.PricelistEngine.prototype;
    models.PricelistEngine = models.PricelistEngine.extend({
        compute_price: function (database, product, partner, qty, pricelist_id) {
            if (!product) {
                return false;
            }
            var promo = product.promo;
            var self = this;
            var db = database;
            var promo_object = false;

            var new_qty = 0;
            // get categories
            var categ_ids = [];
            if (product.categ_id) {
                categ_ids.push(product.categ_id[0]);
                categ_ids = categ_ids.concat(
                    db.product_category_ancestors[product.categ_id[0]]
                );
            }
            // find items
            var items = [], i, len;
            for (i = 0, len = db.pricelist_item_sorted.length; i < len; i++) {
                var item = db.pricelist_item_sorted[i];
                if (
                    (item.product_tmpl_id === false || item.product_tmpl_id[0] === product.product_tmpl_id)
                    && (item.categ_id === false || categ_ids.indexOf(item.categ_id[0]) !== -1)
                    && (
                        (!partner && item.pricelist_id && item.pricelist_id[0] === this.pos.config.pricelist_id[0])
                        || (partner && item.pricelist_id && item.pricelist_id[0] === pricelist_id)
                    )
                ) {
                    items.push(item);
                }
            }
            var results = {};
            results[product.id] = 0.0;
            var price = db.product_by_id[product.id].price;
            // loop through items
            for (i = 0, len = items.length; i < len; i++) {
                var rule = items[i];
                var base_category_object = false;
                if (this.pos.get_order()) {
                    var promo_categories = this.pos.get_order().promo_categories;
                    if (promo_categories) {
                        var current_order_promo_category = promo_categories.find(function(promo){
                            return promo.rule_id === rule.id;
                        });
                        if (current_order_promo_category) {
                            rule.promotional_product_id = [];
                            rule.promotional_product_id.push(current_order_promo_category.product.id);
                            rule.promotional_product_id.push(current_order_promo_category.product.display_name);
                        } else {
                            if (rule.promotional_type === "0_category" && !current_order_promo_category) {
                                rule.promotional_product_id = false;
                            }
                        }
                    } else {
                        if (rule["promotional_pos_category_ids"].length && !current_order_promo_category) {
                            rule.promotional_product_id = false;
                        }
                    }
                }
                var today = new Date();
                var dateoftoday = today.toISOString().substring(0, 10);
                if (promo && promo !== rule.id) {
                    continue;
                }
                if ((rule.date_start !== false && rule.date_start > dateoftoday )
                        ||(rule.date_end !== false && rule.date_end < dateoftoday )) {
                    continue;
                }
                if (!promo) {

                    if (rule.promotional_type === "0_category" && this.pos.get_order()) {
                        if (rule.promotional_product_tmpl_id && rule.promotional_product_tmpl_id[0] == db.product_by_id[product.id].product_tmpl_id) {
                            rule.current_qty = qty;
                        }
                    }
                    if (rule.base_type === "0_category" && this.active_rule(rule)) {
                         continue;
                    } else {
                        if (rule.min_quantity && qty < rule.min_quantity) {
                            continue;
                        }
                        if (rule.base_type && rule["applied_on"] === "4_promotional_product") {
                            if (rule.promotional_product_tmpl_id && rule.promotional_product_tmpl_id[0] != db.product_by_id[product.id].product_tmpl_id) {
                                continue;
                            }
                        }
                        if (rule.product_id && rule.product_id[0]
                            && product.id != rule.product_id[0]) {
                            continue;
                        }
                        if (rule.categ_id) {
                            var cat_id = product.categ_id[0];
                            while (cat_id) {
                                if (cat_id == rule.categ_id[0]) {
                                    break;
                                }
                                cat_id = db.product_category_by_id[cat_id].parent_id[0]
                            }
                            if (!(cat_id)) {
                                continue;
                            }
                        }
                    }
                }
                switch (rule.base) {
                    case 'pricelist':
                        if (rule.base_pricelist_id) {
                            price = self.compute_price(
                                db, product, false, qty,
                                rule.base_pricelist_id[0]
                            );
                        }
                        break;
                    default:
                        if (db.product_by_id[product.id]) {
                            price = db.product_by_id[product.id].price;
                        }
                }
                if (price !== false) {
                    if (!promo && rule["applied_on"] === "5_amount_order_total" && rule["total_discount_product"]) {
                        return db.product_by_id[product.id].price;
                    }
                    var price_limit = price;
                    if (!promo && rule["applied_on"] === "4_promotional_product") {
                        var order = this.pos.get_order();
                        if (order) {
                            if (rule.base_type === "1_product") {
                                new_qty = Number(qty);
                                price = db.product_by_id[product.id].price;
                                promo_object = this.get_promo_object(product, rule, qty, database);
                            }
                        }
                    }
                    else if (rule['price_discount']) {
                        price = ((100.0 - rule['price_discount']) * price)/100.0;
	                } else if (rule['percent_price']) {
		                price = price * ((100.0 - rule['percent_price']) / 100.0);
	                } else if (rule['fixed_price']) {
		                price = rule['fixed_price'];
	                }
                    if (rule['price_round']) {
                        price = parseFloat(price.toFixed(
                                Math.ceil(Math.log(1.0 / rule['price_round'])
                                    / Math.log(10)))
                        );
                    }
                    price += (rule['price_surcharge']
                        ? rule['price_surcharge']
                        : 0.0);
                    if (rule['price_min_margin']) {
                        price = Math.max(
                            price, price_limit + rule['price_min_margin']
                        )
                    }
                    if (rule['price_max_margin']) {
                        price = Math.min(
                            price, price_limit + rule['price_min_margin']
                        )
                    }
                }
                else {
                    break;
                }
            }

            if (promo_object) {
                if (promo_object.category) {
                    var all_categories_rule = false;
                    if (promo_object.base_type === "1_product") {
                        all_categories_rule = this.get_category_rules_by_product_tmpl_id(db, product.product_tmpl_id).filter(function(item) {
                            return item.min_quantity <= new_qty;
                        });
                    }
                    promo_object.category = all_categories_rule;
                    if (promo_object.category) {
                        promo_object.category.forEach(function(category) {
                            category.current_qty = new_qty;
                        });
                    }
                }
                return {
                    price: db.product_by_id[product.id].price,
                    promo: promo_object
                }
            } else {
                return price;
            }
        },
        get_rule_by_id: function(db, id) {
            return db.pricelist_item_by_id[id];
        },
        get_rule_items_by_pricelist_id: function(db, id) {
            return db.pricelist_item_sorted.filter(function(item) {
                return item.pricelist_id[0] === id;
            })
        },
        get_rules_by_product_tmpl_id: function(db, id) {
            var self = this;
            var rules_items = this.get_rule_items_by_pricelist_id(db, this.pos.config.pricelist_id[0]);
            var rules = [];
            rules_items.forEach(function(rule) {
                if (self.active_rule(rule)){
                    if ((rule.promotional_product_tmpl_id && rule.promotional_product_tmpl_id[0] == id)){
                        rules.push(rule);
                    }
                }
            });
            return rules;
        },
        get_rules_by_category_ids: function(db, ids) {
            var self = this;
            var rules_items = this.get_rule_items_by_pricelist_id(db, this.pos.config.pricelist_id[0]);
            var rules = [];
            rules_items.forEach(function(rule) {
                ids.forEach(function(id) {
                    if ((jQuery.inArray(id, rule.base_pos_category_ids) != -1) && self.active_rule(rule)){
                        rules.push(rule);
                    }
                });
            });
            return rules;
        },
        get_promo_object: function(product, rule, qty, db) {
            if (rule.base_type === "1_product" && (product.product_tmpl_id !== rule.promotional_product_tmpl_id[0])) {
                return false;
            }
            var order = this.pos.get_order();
            var promo_object = false;
            var base_product_id = false;

            if (rule.min_quantity && qty >= rule.min_quantity) {
                if (order && order.get_selected_orderline()) {
                    base_product_id = order.get_selected_orderline().id;
                };
                promo_object = {
                    quantity_included: rule.quantity_included,
                    base_product_id: base_product_id,
                    quantity: rule.promotional_product_quantity,
                    rule_id: rule.id,
                    min_quantity: rule.min_quantity,
                    category: rule.promotional_pos_category_ids,
                    product: db.get_product_by_id(rule.promotional_product_id[0]),
                    promotional_type: rule.promotional_type,
                    base_type: rule.base_type,
                }
                return promo_object;
            }
        },
        get_category_rules_by_product_tmpl_id: function(db, id) {
            var self = this;
            var rules = this.get_rules_by_product_tmpl_id(db, id);
            var current_rules = [];
            rules.forEach(function(rule) {
                if (self.active_rule(rule) && rule.promotional_type === "0_category") {
                    current_rules.push(rule);
                }
            });
            return current_rules;
        },
        get_orderlines_by_base_category_ids: function(db, ids){
            var order = this.pos.get_order();
            var lines = order.get_orderlines();
            var base_category_lines = [];
            lines.forEach(function(line) {
                var res = line.product.pos_category_ids.find(function(item) {
                    return jQuery.inArray(item, ids) != -1;
                });
                if (res && !line.promo) {
                    base_category_lines.push(line)
                }
            });
            return base_category_lines;
        },
        update_products_ui: function (partner) {
            var db = this.db;
	        var product_list_ui = $('.product-list .product');
            for (var i = 0, len = product_list_ui.length; i < len; i++) {
                var product_ui = product_list_ui[i];
                var product_id = $(product_ui).data('product-id');
                var product = $.extend({}, db.get_product_by_id(product_id));
                var rules = db.find_product_rules(product);
                var quantities = [];
                quantities.push(1);
                for (var j = 0; j < rules.length; j++) {
                    if ($.inArray(rules[j].min_quantity, quantities) === -1) {
                        quantities.push(rules[j].min_quantity);
                    }
                }
                quantities = quantities.sort();
                var prices_displayed = '';
                for (var k = 0; k < quantities.length; k++) {
                    var qty = quantities[k];
                    var price = this.compute_price_all(
                        db, product, partner, qty
                    );
                    if (typeof price  === "object" && price.promo) {
                        var rule = this.get_rule_by_id(db, price.promo.rule_id);
                        if (rule && rule["applied_on"] === "4_promotional_product") {
                            price = product.price;
                        }
                    }
                    if (product.promo) {
                        var rule = this.get_rule_by_id(db, product.promo);
                        if (rule && rule["applied_on"] === "4_promotional_product") {
                            price = product.price;
                        }
                    }
                    if (price !== false) {
                        if (this.pos.config.display_price_with_taxes) {
                            var prices = this.simulate_price(
                                product, partner, price, qty
                            );
                            price = prices['priceWithTax']
                        }
                        price = round_di(parseFloat(price)
                            || 0, this.pos.dp['Product Price']);
                        var product_screen_widget = new screens.ProductScreenWidget(this, {});
                        price = product_screen_widget.format_currency(price);
                        if (k == 0) {
                            $(product_ui).find('.price-tag').html(price);
                        }
                        prices_displayed += qty
                            + 'x &#8594; ' + price + '<br/>';
                    }
                }
                if (prices_displayed != '') {
                    $(product_ui).find('.price-tag').attr(
                        'data-original-title', prices_displayed
                    );
                    $(product_ui).find('.price-tag').attr(
                        'data-toggle', 'tooltip'
                    );
                    $(product_ui).find('.price-tag').tooltip(
                        {delay: {show: 50, hide: 100}}
                    );
                }
            }
        },
        //  active rule in current time
        active_rule: function(rule) {
            var today = new Date();
            var dateoftoday = today.toISOString().substring(0, 10);
            if ((rule.date_start !== false && rule.date_start < dateoftoday )
               ||(rule.date_end !== false && rule.date_end > dateoftoday )
               ||(rule.date_end === false && rule.date_start === false )){
                    return true;
            }
        },
    });
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes, options){
            var self = this;
            this.order_total_discount_product_id = false;
            _super_order.initialize.apply(this, arguments);
            this.compute_new_discount_price = true;
            if (!this.old_base_categories) {
                this.old_base_categories = {};
            }
            if (!this.promo_categories) {
                this.promo_categories = [];
            }
            this.promo_categories = [];
            this.show_popup = false;
            if (!this.promo_orderlines_obj) {
                this.promo_orderlines_obj = [];
            }
        },
        add_product: function(product, options) {
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            this.compute_new_discount_price = true;
            var current_productline = this.get_selected_orderline();
            var last_orderline = this.get_last_orderline();

            if (this.is_empty() && this.order_total_discount_product_id && this.order_total_discount_product_id.length) {
                this.order_total_discount_product_id = false;
            }
            var barcode_quantity = options.quantity;
            if (options.quantity) {
                options.quantity = false;
            }
            var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});
            // get existing base product (which has promo_product_id)
            var base_orderline = this.get_base_orderline(product, line.quantity);
            if (base_orderline && !base_orderline.promo) {
                base_orderline.merge(line);
                this.select_orderline(base_orderline);
            } else if ((current_productline && current_productline.product_is_promo && !this.promo) ||
                (last_orderline && last_orderline.promo)) {
                this.orderlines.add(line);
                this.select_orderline(this.get_last_orderline());
            } else {
                _super_order.add_product.apply(this, arguments);
            }
            // if min quantity is 1, then create new promo line after adding current order line
            if (this.promo && this.promo.min_quantity === 1) {
                current_productline = this.get_selected_orderline();
                if (current_productline.quantity === 1) {

                    if (this.promo.promotional_type === "1_product") {
                        if (this.promo.quantity_included) {
                            current_productline.change_qty = false;
                        }
                        current_productline.add_promo_product(this.promo.product, this.promo.rule_id, this.promo.quantity, this.promo.quantity_included);
                    }
                    if (this.promo.promotional_type === "0_category") {
                        var rule = this.pos.pricelist_engine.get_rule_by_id(this.pos.db, this.promo.rule_id);
                        this.open_promo_product_popup([rule]);
                    }
                    this.select_orderline(current_productline);
                }
            }
            this.promo = false;
            // if using barcode then set new quantity for current order line
            if (barcode_quantity) {
                var current_qty = barcode_quantity;
                // If the order line exists then change the amount of this order line
                if (base_orderline) {
                    current_qty = current_qty + (base_orderline.quantity - line.quantity);
                }
                this.get_selected_orderline().set_quantity(current_qty);
            }
            // scroll to selected order line
            var width = this.get_orderlines().indexOf(this.get_selected_orderline())
            if (base_orderline) {
                width = this.get_orderlines().indexOf(base_orderline);
            }
            if (width > -1) {
                $('.order-scroller').scrollTop(50 * width);
            }
        },
        select_orderline: function(line){
            if(line){
                if (!line.discount_product && !line.promo) {
                     _super_order.select_orderline.apply(this, arguments);
                }
            } else {
                _super_order.select_orderline.apply(this, arguments);
            }
        },
        get_base_orderline: function(product, quantity){
            var orderlines = this.get_orderlines();
            var base_orderline = false;
            var self = this;
            if (orderlines) {
                var base_orderlines = orderlines.filter(function(item){
                    var rules = self.pos.pricelist_engine.get_rules_by_product_tmpl_id(self.pos.db, item.product.product_tmpl_id);
                    var product_rules = rules.filter(function(rule){
                        return rule.applied_on === "4_promotional_product";
                    });
                    if (product_rules.length) {
                        return true;
                    }
                });
                if (base_orderlines) {
                    base_orderline = base_orderlines.find(function(item){
                        return item.product.id === product.id && !item.promo;
                    });
                    if (!base_orderline) {
                        var rules = this.pos.pricelist_engine.get_rules_by_category_ids(this.pos.db, product.pos_category_ids);
                        if (rules && rules.length) {
                            base_orderline = this.get_orderlines_by_product_id(product.id);
                            base_orderline = base_orderline.find(function(item){
                                return !item.promo;
                            });
                        }
                    }
                    if (base_orderline) {
                        var promo = this.get_orderline(base_orderline.promo_product_id)
                        if (promo) {
                            var rule = this.pos.pricelist_engine.get_rule_by_id(this.pos.db, promo.promo);
                            if ((base_orderline.quantity + quantity + promo.quantity) % rule.min_quantity == 0) {
                                base_orderline.change_qty = true;
                                base_orderline.old_qty = base_orderline.quantity + quantity  + promo.quantity;
                            } else {
                                base_orderline.change_qty = false;
                            }
                        }
                    }
                }
            }
            return base_orderline;
        },
        get_change: function(paymentline) {
            this.change_base_promotional_rule();
            return _super_order.get_change.apply(this, arguments);
        },
        change_base_promotional_rule: function(){
            var self = this;
            var categories = [];
            if (!this.is_empty() && this.get_selected_orderline()) {
                var current_orderline = this.get_selected_orderline();
                var rules_items = this.pos.pricelist_engine.get_rule_items_by_pricelist_id(this.pos.db, this.pos.config.pricelist_id[0]);

                //  get base_type is category rules only
                var rules = rules_items.filter(function(rule) {
                    return rule.base_type === "0_category" && self.pos.pricelist_engine.active_rule(rule);
                });

                //  filter all rules with current product
                rules = rules.filter(function(rule) {
                    var res = false;
                    current_orderline.product.pos_category_ids.forEach(function(id) {
                        if (jQuery.inArray(id, rule.base_pos_category_ids) != -1) {
                            res = true;
                        }
                    })
                    return res;
                });

                var len = rules.length;
                for (var i = 0; i < len; i++) {
                    var rule = rules[i];
                    rule.current_qty = false;
                    rule.current_orderline = current_orderline;
                    var base_category_orderlines = [current_orderline];
                    var base_category_quantity = 0;
                    if (rule.cumulative_quantity) {
                        base_category_orderlines = this.pos.pricelist_engine.get_orderlines_by_base_category_ids(this.pos.db, rule.base_pos_category_ids);
                    }
                    base_category_orderlines.forEach(function(line) {
                        base_category_quantity = base_category_quantity + line.quantity;
                    });
                    var exist_promo_line = false;
                    if (base_category_quantity < rule.min_quantity) {
                        if (this.promo_orderlines_obj) {
                            exist_promo_line = this.promo_orderlines_obj.find(function(line) {
                                return line.promo_product_id == rule.promotional_product_id[0];
                            });
                            if (exist_promo_line) {
                                this.change_promo_quantity(base_category_quantity, rule, exist_promo_line);
                            }
                        }
                    }
                    if (!rule.cumulative_quantity) {
                        self.remove_promo_line_by_base_orderline(current_orderline);
                    }
                    var promo_obj = this.pos.pricelist_engine.get_promo_object(false, rule, base_category_quantity, this.pos.db);
                    if (promo_obj && rule.promotional_type === "1_product") {
                        exist_promo_line = false;
                        if (rule.cumulative_quantity) {
                            if (this.promo_orderlines_obj) {
                                exist_promo_line = this.promo_orderlines_obj.find(function(line) {
                                    return line.promo_product_id == promo_obj.product.id;
                                });
                            }
                        } else {
                            exist_promo_line = this.promo_orderlines_obj.find(function(line){
                                return line.base_product_line_id === current_orderline.id;
                            });
                        }
                        //  if is exist promo line set new quantity, else create new promo object
                        if (exist_promo_line) {
                            this.change_promo_quantity(base_category_quantity, rule, exist_promo_line);
                        } else if (this.promo_orderlines_obj) {
                            this.add_promo_product(promo_obj.product, promo_obj.rule_id, promo_obj.quantity, rule.base_pos_category_ids, rule.min_quantity);
                        }
                    } else if (rule.promotional_type === "0_category") {
                        if (!rule.cumulative_quantity && base_category_quantity < rule.min_quantity) {
                            continue;
                        }
                        rule.current_qty = base_category_quantity;
                        rule.order_promo = true;
                        categories.push(rule);
                    }
                }
                if (categories && categories.length) {
                    this.call_promo_category(categories);
                }
            }
        },
        remove_promo_line_by_base_orderline: function(base_line) {
            var self = this;
            var exist_promolines = this.get_orderlines().filter(function(line){
                return line.base_product_line_id === base_line.id && line.min_quantity > base_line.quantity;
            });
            if (!exist_promolines.length) {
                return false;
            }
            exist_promolines.forEach(function(line) {
                self.remove_orderline(line);
            });
            this.select_orderline(base_line);
        },
        add_promo_product: function(product, rule_id, quantity, category_ids, min_quantity) {
            var self = this;
            var promo_line = new models.Orderline({}, {
                pos: this.pos,
                order: this,
                product: product,
                promo: rule_id,
                base_category_ids: category_ids,
                base_order_id: this.id,
                base_product_line_id: self.get_selected_orderline().id || false,
                min_quantity: min_quantity,
            });
            promo_line.product_is_promo = true;
            this.promo_orderlines_obj.push({
                promo_orderline_id: promo_line.id,
                promo_product_id: promo_line.product.id,
                category_ids: category_ids,
                base_product_line_id: self.get_selected_orderline().id || false,
            });
            promo_line.set_quantity(quantity);
            this.orderlines.add(promo_line);
        },
        change_promo_quantity: function(qty, rule, promo) {
            if (!rule.cumulative_quantity) {
                return false;
            }
            var self = this;
            var rule = this.pos.pricelist_engine.get_rule_by_id(this.pos.db, rule.id);
            var multi_quantity = Math.floor(qty / rule.min_quantity);
            var quantity = multi_quantity * rule.promotional_product_quantity;
            var line = this.get_orderline(promo.promo_orderline_id);
            if (quantity) {
                if (line.quantity === quantity) {
                    return false;
                } else {
                    line.set_quantity(quantity);
                }
            } else {
                //  remove current promo orderline
                this.promo_orderlines_obj.forEach(function(item, index) {
                    if (item.promo_product_id === line.product.id) {
                        self.promo_orderlines_obj.splice(index, 1);
                    }
                })
                this.remove_orderline(line);
            }
        },
        call_promo_category: function(categories) {
            var self = this;
            var current_categories_object = [];
            categories.forEach(function(rule) {
                var current_categories = [];
                var base_category_quantity = 0;
                if (rule.cumulative_quantity) {
                    var base_category_orderlines = self.pos.pricelist_engine.get_orderlines_by_base_category_ids(self.pos.db, rule.base_pos_category_ids);
                    base_category_orderlines.forEach(function(line) {
                        base_category_quantity = base_category_quantity + line.quantity;
                    });
                } else {
                    base_category_quantity = rule.current_qty;
                }

                var multi_quantity = Math.floor(base_category_quantity / rule.min_quantity);
                var i = 1;
                if (!rule.cumulative_quantity) {
                    current_categories.push(rule);
                } else {
                    while (i <= multi_quantity) {
                        var new_rule = Object.assign({}, rule);
                        new_rule.min_quantity = i * rule.min_quantity;
                        current_categories.push(new_rule);
                        i++;
                    }
                }
                current_categories_object.push({rule_id: rule.id, categories: current_categories});
            });

            var new_categories = [];
            var old_line_ids = [];
            current_categories_object.forEach(function(item) {
                if (!self.old_base_categories || self.is_empty()) {
                    return false;
                }
                var rule = self.pos.pricelist_engine.get_rule_by_id(self.pos.db, item.rule_id);
                if (!rule.cumulative_quantity) {
                    var current_orderline = self.get_selected_orderline();
                    if (rule.min_quantity > current_orderline.quantity){
                        return false;
                    }

                    var exist_promolines = self.get_orderlines().filter(function(line){
                        return line.base_product_line_id === current_orderline.id;
                    });

                    if (exist_promolines.length) {
                        var new_promo_category = [];
                        item.categories.forEach(function(c) {
                            if (exist_promolines && exist_promolines.length) {
                                var res = exist_promolines.find(function(line) {
                                    return line.min_quantity == c.min_quantity;
                                });
                                if (!res) {
                                    new_categories.push(c);
                                }
                            }
                        });
                    } else {
                        item.categories.forEach(function(category) {
                            new_categories.push(category);
                        });
                    }
                } else {
                    var old_categories = self.old_base_categories[item.rule_id];
                    if (!old_categories) {
                        self.old_base_categories[item.rule_id] = item.categories;
                        item.categories.forEach(function(category) {
                            new_categories.push(category);
                        });
                    } else if (old_categories.length < item.categories.length) {
                        self.old_base_categories[item.rule_id] = item.categories;
                        var current_base_category = item.categories.concat();
                        old_categories.forEach(function(category){
                            var current_index = false;
                            var res = current_base_category.find(function(element, index) {
                                if (element.min_quantity === category.min_quantity) {
                                    current_index = index;
                                    return true;
                                }
                            });
                            if (res) {
                                current_base_category.splice(current_index, 1);
                            }
                        });
                        current_base_category.forEach(function(category) {
                            new_categories.push(category);
                        });
                    } else if (old_categories.length > item.categories.length) {
                        rule = self.pos.pricelist_engine.get_rule_by_id(self.pos.db, item.rule_id);
                        var base_category_orderlines = self.pos.pricelist_engine.get_orderlines_by_base_category_ids(self.pos.db, rule.base_pos_category_ids);
                        var base_category_quantity = 0;
                        base_category_orderlines.forEach(function(line) {
                            base_category_quantity = base_category_quantity + line.quantity;
                        });
                        var exist_line = self.get_promo_products_in_order_by_rule_id(rule.id).filter(function(line){
                            return line.min_quantity > base_category_quantity;
                        });
                        exist_line.forEach(function(line){
                            old_line_ids.push(line.id);
                        });
                        self.old_base_categories[item.rule_id] = item.categories;
                    }
                }
            });
            new_categories = _.sortBy(new_categories, 'min_quantity');
            if (new_categories && new_categories.length) {

                this.open_promo_product_popup(new_categories);
            }
            if (old_line_ids && old_line_ids.length) {
                var order = this.pos.get_order();
                old_line_ids.forEach(function(line_id){
                    self.remove_orderline(order.get_orderline(line_id));
                });
            }
        },
        get_old_base_category_len: function(rule_id) {
            return this.old_base_categories_len.find(function(rule){
                return rule.rule_id === rule_id;
            });
        },
        get_promo_products_in_order_by_rule_id: function(id) {
            return this.get_orderlines().filter(function(line) {
                return line.promo && line.promo === id;
            });
        },
        get_total_with_tax: function() {
            var total_with_tax = this.get_total_without_tax() + this.get_total_tax();
            this.get_amount_order_discount_rule(total_with_tax);
            return _super_order.get_total_with_tax.apply(this, arguments);
        },
        get_all_promoline_by_base_line_id: function(id) {
            return this.get_orderlines().filter(function(line){
                return line.base_product_id === id;
            })
        },
        get_amount_order_discount_rule: function(price) {
            var self = this;
            var rules = [];
            var partner = this ? this.get_client() : null;
            var self = this;
            var price_limit = price;
            var total_price = price_limit;
            if (this.order_total_discount_product_id && this.compute_new_discount_price) {
                var line = this.get_orderline(this.order_total_discount_product_id);
                if (line) {
                    price = price + (-line.price );
                    total_price = price;
                }
            }
            if (this.pos) {
                this.pos.db.pricelist_item_sorted.forEach(function (item) {
                    if ((!partner && item.pricelist_id && item.pricelist_id[0] === self.pos.config.pricelist_id[0]) && item["applied_on"] === "5_amount_order_total") {
                        if (self.pos.pricelist_engine.active_rule(item) && item.amount_order_total <= price) {
                            rules.push(item);
                        }
                    }
                });
            }
            function compareNumeric(a, b) {
                if (a.amount_order_total < b.amount_order_total) return 1;
                if (a.amount_order_total > b.amount_order_total) return -1;
            }
            rules.sort(compareNumeric);
            if (rules.length === 0 && this.compute_new_discount_price && this.order_total_discount_product_id) {
                var line = this.get_orderline(this.order_total_discount_product_id);
                if (line) {
                    this.remove_orderline(line);
                }
                this.order_total_discount_product_id = false;
            }
            var discount_product_price = 0;
            if (rules.length) {
                rules.forEach(function(item, index) {
                    var rule = rules[index];
                    if (rule['price_discount']) {
                        price = price * ((100.0 - rule['price_discount']) / 100.0);
                    } else if (rule['percent_price']) {
                        price = price * ((100.0 - rule['percent_price']) / 100.0);
                    } else if (rule['fixed_price']) {
                        price = rule['fixed_price'];
                    }
                    if (rule['price_round']) {
                        price = parseFloat(price.toFixed(
                            Math.ceil(Math.log(1.0 / rule['price_round'])
                                / Math.log(10)))
                        );
                    }
                    price += (rule['price_surcharge']
                        ? rule['price_surcharge']
                        : 0.0);
                    if (rule['price_min_margin']) {
                        price = Math.max(
                            price, price_limit + rule['price_min_margin']
                        )
                    }
                    if (rule['price_max_margin']) {
                        price = Math.min(
                            price, price_limit + rule['price_min_margin']
                        )
                    }
                    discount_product_price = discount_product_price + (total_price - price);
                    price = total_price;
                });
                var rule = rules[0];
                var total_discount_product = this.pos.db.get_product_by_id(rule.total_discount_product[0]);
                var discount_product = this.get_discount_orderline();
                    if (discount_product && this.get_orderlines().length > 1) {
                        this.order_total_discount_product_id = discount_product.id
                    } else {
                        this.order_total_discount_product_id = false;
                    }
                if (!this.order_total_discount_product_id && !discount_product) {
                    total_discount_product.price = - discount_product_price;
                    var last_orderline = this.get_last_orderline();
                    var line = new models.Orderline({}, {pos: this.pos, order: this, product: total_discount_product, discount_product: true});
                    this.order_total_discount_product_id = line.id;
                    this.orderlines.add(line);
                    this.select_orderline(last_orderline);
                    this.compute_new_discount_price = false;
                } else if (this.order_total_discount_product_id && this.compute_new_discount_price && this.get_orderline(this.order_total_discount_product_id)) {
                    this.compute_new_discount_price = false;
                    var line = this.get_orderline(this.order_total_discount_product_id);
                    line.price = - discount_product_price;
                    line.trigger('change', line);
                }
            }
        },
        get_discount_orderline: function() {
            //  get order line in which the product - discount product
            return this.get_orderlines().find(function(item) {
                return item.discount_product === true;
            })
        },
        get_all_orderlines_without_discount: function() {
            // get all orderlines without the discount line
            var discount_line = this.get_discount_orderline();
            if (discount_line) {
                return this.get_orderlines().filter(function(item){
                    return item.id != discount_line.id;
                })
            }
        },
        open_promo_product_popup: function(all_category_rules) {
            if (!all_category_rules.length) {
                return false;
            }
            var self = this;
            if (!this.show_popup) {
                this.pos.ready.then(function(){
                    self.show_popup = true;
                    self.open_promo_product_popup(all_category_rules);
                });
            } else {
                var self = this;
                var category_rules = _.sortBy(all_category_rules, 'min_quantity');
                var category = category_rules[0];
                this.pos.gui.show_popup('promo_category', {
                    title: _t("Promo Category Discount"),
                    rule_id: category.id,
                    quantity: category.promotional_product_quantity,
                    quantity_included: category.quantity_included,
                    category_ids: category.promotional_pos_category_ids,
                    order_promo: category.order_promo,
                    min_quantity: category.min_quantity,
                    confirm: function () {
                        category_rules.splice(0, 1);
                        self.open_promo_product_popup(category_rules);
                    },
                });
            }
        },
        get_orderlines_by_product_id: function(id) {
            return this.get_orderlines().filter(function(line){
                return line.product.id === id;
            });
        },
        get_promo_category: function(promo_obj) {
            var categories_rule = promo_obj.category.filter(function(rule) {
                return rule.current_qty % rule.min_quantity == 0;
            });
            categories_rule = _.sortBy(categories_rule, 'min_quantity');
            if (categories_rule[categories_rule.length - 1]) {
                return [categories_rule[categories_rule.length - 1]];
            }
        },
        export_for_printing: function(){
            var receipt = _super_order.export_for_printing.apply(this, arguments);
            var discount_orderline = this.get_discount_orderline()
            if (discount_orderline) {
                var orderlines = [];
                var self = this;
                this.get_all_orderlines_without_discount().forEach(function(orderline){
                    orderlines.push(orderline.export_for_printing());
                });
                var subtotal = this.get_subtotal() -discount_orderline.price;
                var total_discount = this.get_total_discount() + (-discount_orderline.price);
                receipt.subtotal = subtotal;
                receipt.total_discount = total_discount;
            }
            return receipt;
        },
        init_from_JSON: function(json) {
            this.order_total_discount_product_id = json.order_total_discount_product_id;
            this.promo_categories = json.promo_categories;
            this.old_base_categories = json.old_base_categories;
            this.promo_orderlines_obj = json.promo_orderlines_obj;
            _super_order.init_from_JSON.call(this, json);
        },
        export_as_JSON: function() {
            var data = _super_order.export_as_JSON.apply(this, arguments);
            data.order_total_discount_product_id = this.order_total_discount_product_id;
            data.promo_categories = this.promo_categories;
            data.old_base_categories = this.old_base_categories;
            data.promo_orderlines_obj = this.promo_orderlines_obj;
            return data;
        }
    });
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            this.change_qty = true;
            this.promo = options.promo || false;
            this.pricelist_rule_id =  options.pricelist_rule_id || false;
            this.promo_product_id = options.promo_product_id || false;
            this.base_product_id = options.base_product_id || false;
            this.quantity_included = options.quantity_included || false;
            this.discount_product = options.discount_product || false;
            this.min_quantity = options.min_quantity || false;
            this.base_product_line_id = options.base_product_line_id;
            var result = _super_orderline.initialize.apply(this, arguments);
            this.product_is_promo = false;
            if (this.product !== undefined) {
                var qty = this.compute_qty(this.order, this.product);
                var partner = this.order ? this.order.get_client() : null;
                var product = this.product;
                var db = this.pos.db;
                product.promo = this.promo;
                var price = this.pos.pricelist_engine.compute_price_all(
                    db, product, partner, qty
                );
                if (typeof price  === "object" && price.promo) {
                    var promo = price.promo;
                    price = price.price;
                    this.order.promo = promo;
                    this.pricelist_rule_id = promo.rule_id;
                }
                if (price !== false) {
	                this.price = round_di(parseFloat(price) || 0, this.pos.dp['Product Price']);
                }
            }
            if (this.base_product_id) {
                var base_product = this.order.get_orderline(this.base_product_id);
                if (base_product) {
                    base_product.promo_product_id = this.id;
                }
            }
            return result;
        },
        set_quantity: function (quantity) {
            var self = this;
            var promo_obj = false;
            var partner = this.order ? this.order.get_client() : null;
            var product = this.product;
            var db = this.pos.db;
            var old_price = 0;
            if (this.get_quantity()) {
                product.promo = this.promo;
                old_price = this.pos.pricelist_engine.compute_price_all(
                    db, product, partner, this.get_quantity()
                );
                if (typeof old_price === "object") {
                    old_price = old_price.price;
                }
            }
            _super_orderline.set_quantity.apply(this, arguments);
            var price = this.pos.pricelist_engine.compute_price_all(
                db, product, partner, quantity
            );
            if (typeof price === "object") {
                promo_obj = price.promo;
                price = price.price;
            }
            if (!this.promo && price !== false) {
	            this.set_unit_price(price);
            }

            //  add new promo product
            if (!this.promo && promo_obj) {
                if (promo_obj.promotional_type === "0_category") {
                    var categories = promo_obj.category.slice();
                    var current_categories = [];
                    categories.forEach(function(rule) {
                        if (rule.cumulative_quantity) {
                            var multi_quantity = Math.floor(rule.current_qty / rule.min_quantity);
                            var i = 1;
                            while (i <= multi_quantity) {
                                var new_rule = Object.assign({}, rule);
                                new_rule.min_quantity = i * rule.min_quantity;
                                current_categories.push(new_rule);
                                i++;
                            }
                        } else {
                            current_categories.push(rule);
                        }
                    });
                    current_categories = _.sortBy(current_categories, 'min_quantity');
                    if (!this.old_category_length || this.old_category_length < current_categories.length) {
                        var current_len = current_categories.length;
                        if (current_len > 1) {
                            current_categories.splice(0, this.old_category_length);
                        }
                        this.old_category_length = current_len;
                        this.order.open_promo_product_popup(current_categories);
                    } else if (this.old_category_length > current_categories.length) {
                        var all_product_rules = this.pos.pricelist_engine.get_rules_by_product_tmpl_id(this.pos.db, this.product.product_tmpl_id);
                        var old_promo_lines = [];
                        all_product_rules.forEach(function(rule, index){
                            var exist_lines = self.order.get_promo_products_in_order_by_rule_id(rule.id).filter(function(line) {
                                return line.min_quantity > rule.current_qty;
                            });
                            exist_lines.forEach(function(line) {
                                old_promo_lines.push(line);
                            });
                        });
                        old_promo_lines.forEach(function(line) {
                            self.order.remove_orderline(line);
                        });
                        var new_len = 0;
                        all_product_rules.forEach(function(rule) {
                            var exist_lines = self.order.get_promo_products_in_order_by_rule_id(rule.id);
                            new_len = new_len + exist_lines.length;
                        });
                        this.old_category_length = new_len;
                    }
                } else if (!this.promo_product_id && promo_obj.promotional_type === "1_product") {
                    this.old_qty = this.quantity;
                    this.add_promo_product(promo_obj.product, promo_obj.rule_id, promo_obj.quantity, promo_obj.quantity_included, promo_obj.min_quantity);
                    this.order.select_orderline(this);
                }
            }

            //  The quantity of the base product varies, it is necessary to count the number
            //  of promo products
            var rule = this.pos.pricelist_engine.get_rule_by_id(this.pos.db, promo_obj.rule_id);

            if (this.promo_product_id && this.order.get_orderline(this.promo_product_id) && rule.cumulative_quantity) {
                var promo_product = this.order.get_orderline(this.promo_product_id);
                if (!promo_product.quantity_included) {
                    if (promo_obj && promo_obj.product && (!promo_obj.category || !promo_obj.category.length)) {
                        promo_product.set_promo_product_quantity(quantity);
                    } else if (!promo_obj) {
                        promo_product.set_promo_product_quantity(quantity);
                    }
                } else {
                    if (this.change_qty) {
                        promo_product.set_promo_product_quantity(this.old_qty);
                    }
                }
            }
        },
        add_promo_product: function(product, rule_id, quantity, quantity_included, min_quantity){
            var self = this;
            var promo_line = new models.Orderline({}, {
                pos: this.pos,
                order: this.order,
                product: product,
                promo: rule_id,
                quantity_included: quantity_included,
                base_product_id: this.id,
                min_quantity: min_quantity,
            });
            promo_line.product_is_promo = true;
            promo_line.set_quantity(quantity);
            this.order.orderlines.add(promo_line);
            if (quantity_included) {
                this.set_quantity_base_product(this.id, quantity, false);
            }
        },
        set_quantity_base_product: function(base_product_id, promo_product_qty, change) {
            change = change || false;
            var new_qty = 0;
            var base_product_line = this.order.get_orderline(base_product_id);
            if (base_product_line) {
                if (change) {
                    new_qty = base_product_line.old_qty - promo_product_qty;
                    base_product_line.change_qty = false;
                    if (new_qty >= 0) {
                        base_product_line.set_quantity(new_qty);
                        base_product_line.change_qty = true;
                    }
                } else {
                    new_qty = base_product_line.quantity - promo_product_qty;
                    if (new_qty >= 0) {
                        base_product_line.set_quantity(new_qty);
                    }
                }
            }
        },
        set_promo_product_quantity: function(base_product_quantity) {
            var self = this;
            var quantity = this.get_promo_product_quantity(base_product_quantity);
            if (quantity) {
                this.set_quantity(quantity);
                if (this.quantity_included) {
                    this.set_quantity_base_product(this.base_product_id, quantity, true);
                }
            } else {
                var promo_lines = this.order.get_all_promoline_by_base_line_id(this.base_product_id);
                promo_lines.forEach(function(line) {
                    self.remove_promo_product(line);
                });
            }
        },
        get_promo_product_quantity: function(base_product_quantity){
            var rule = this.pos.pricelist_engine.get_rule_by_id(this.pos.db, this.promo);
            if (rule.min_quantity > base_product_quantity) {
                return false;
            }
            var multi_quantity = 0;
            if (this.quantity_included) {
                multi_quantity = Math.floor(base_product_quantity / rule.min_quantity);
            } else {
                multi_quantity = Math.floor(base_product_quantity / rule.min_quantity);
            }
            var quantity = multi_quantity * rule.promotional_product_quantity;
            if (!quantity) {
                return false;
            }
            return quantity;
        },
        remove_promo_product: function(line) {
            var base_product = this.order.get_orderline(line.base_product_id);
            base_product.promo_product_id = false;
            base_product.product.promo = false;
            var current_order_promo_category = this.order.promo_categories;
            if (current_order_promo_category) {
                var promo_category = current_order_promo_category.find(function(promo) {
                    return promo.product.id === line.product.id;
                });
                if (promo_category) {
                    var promo_index = current_order_promo_category.indexOf(promo_category);
                    if (promo_index >=0) {
                        this.order.promo_categories.splice(promo_index, 1)
                    }
                }
            }
            this.order.remove_orderline(line);
            base_product.old_category_length = false;
        },
        init_from_JSON: function(json) {
            this.product_is_promo = json.product_is_promo;
            this.promo = json.promo;
            this.promo_product_id = json.promo_product_id;
            this.base_product_id = json.base_product_id;
            this.quantity_included = json.quantity_included;
            this.discount_product = json.discount_product;
            this.min_quantity = json.min_quantity;
            this.old_category_length = json.old_category_length;
            this.base_product_line_id = json.base_product_line_id;
            _super_orderline.init_from_JSON.call(this, json);
        },
        export_as_JSON: function(){
            var data = _super_orderline.export_as_JSON.apply(this, arguments);
            data.product_is_promo = this.product_is_promo;
            data.promo = this.promo;
            data.promo_product_id = this.promo_product_id;
            data.base_product_id = this.base_product_id;
            data.quantity_included = this.quantity_included;
            data.discount_product = this.discount_product;
            data.min_quantity = this.min_quantity;
            data.old_category_length = this.old_category_length;
            data.base_product_line_id = this.base_product_line_id;
            return data;
        }
    });
});
