/* Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_product_sync.pos', function (require) {

    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var DB = require('point_of_sale.DB');
    var rpc = require('web.rpc');

    models.load_fields('product.product',['available_in_pos']);

    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function(){
            PosModelSuper.prototype.initialize.apply(this, arguments);
            this.bus.add_channel_callback("pos_product_sync", this.on_barcode_updates, this);
        },
        on_barcode_updates: function(data){
            var self = this;
            if (data.message === 'update_product_fields' && data.product_ids && data.product_ids.length) {
                if (data.action && data.action === 'unlink') {
                    this.remove_unlinked_products(data.product_ids);
                } else {
                    this.reload_products(data.product_ids).then(function(){
                        self.update_product_related_templates(data.product_ids);
                    });
                }
            }
        },

        reload_products: function(ids) {
            var def = new $.Deferred();
            if (!ids) {
                return def.reject();
            }
            var self = this;
            var model_name = 'product.product';
            var product_model = _.find(this.models,function(model){
                return model.model === model_name;
            });
            ids = Array.isArray(ids)
            ? ids
            : [ids];
            return rpc.query({
                model: model_name,
                method: 'read',
                args: [ids, product_model.fields],
            }, {
                shadow: true,
            }).then(function(products) {
                product_model.loaded(self, products)
            }, function(err,event){
                if (err) {
                    console.log(err.stack);
                }
                event.preventDefault();
            });
        },

        get_all_orders_orderlines: function() {
            return _.chain(this.get_order_list())
                .map(function(o){
                    return o.get_orderlines();
                })
                .flatten().value();
        },

        update_product_related_templates: function(product_ids) {
            var self = this;

            // Product Item
            var product_screen = this.gui.screen_instances.products;
            var product_list_widget = product_screen.product_list_widget;
            product_list_widget.update_product_item(product_ids);

            // Orderlines
            this.update_orderlines(product_ids);

            // product Images
            _.each(product_ids, function(pid) {
                self.update_image(pid);
            });
        },

        update_image: function(pid) {
            var self = this;
            var image_url = window.location.origin + '/web/image?model=product.product&field=image_medium&id=' + pid;
            var product = this.db.get_product_by_id(pid);
            return this._convert_product_img_to_base64(product, image_url);
        },

        update_orderlines: function (product_ids) {
            var self = this;
            var product_screen = this.gui.screen_instances.products;
            return _.chain(this.get_all_orders_orderlines())
            .filter(function(ol) {
                return _.contains(product_ids, ol.get_product().id);
            })
            .each(function(ol) {
                ol.product = self.db.get_product_by_id(ol.product.id);
                product_screen.order_widget.rerender_orderline(ol);
            }).value();
        },

        remove_unlinked_products(product_ids) {
            // probably its impossible case
            var self = this;

            // Product Item
            var product_screen = this.gui.screen_instances.products;
            var product_list_widget = product_screen.product_list_widget;
            product_list_widget.update_product_item(product_ids, 'remove');

            // Orderlines
            var orderlines = _.filter(this.get_all_orders_orderlines(), function(ol) {
                return _.contains(product_ids, ol.get_product().id);
            });
            var orderline = false;
            while ( i < orderlines.length ) {
                orderline = orderlines[i];
                orderline.order.remove_orderline(orderline);
            }

            // DB
            _.each(product_ids, function(p_id){
                var product = self.db.products_by_id[p_id];
                if (product.barcode) {
                    delete self.db.products_by_barcode[product.barcode];
                }
                delete self.db.products_by_id[p_id]
            });
        },
    });

    screens.ProductListWidget.include({
        update_product_item: function(product_ids, mode) {
            var self = this;
            var product_list = this.product_list;
            var product = false;
            _.each(product_ids, function(prod_id) {
                index = _.indexOf(product_list, _.find(product_list, function(p){
                    return p.id == prod_id;
                }));
                index = index > -1
                ? index
                : product_list.length
                product = self.pos.db.get_product_by_id(prod_id);
                if (product.available_in_pos && mode !== 'remove') {
                    product_list[index] = product;
                } else {
                    product_list.splice(index, 1);
                }
                // clear cache
                _.chain(self.product_cache.cache)
                .keys()
                .filter(function(k){
                    return k.includes(prod_id);
                })
                .each(function(k){
                    self.product_cache.clear_node(k);
                }).value();
            });
            self.set_product_list(product_list);
        },
    });

    DB.include({
        add_products: function(products){
            // the function is overriden in order to prevent the product replacement for example after payment
            var already_downloaded_products = [];
            if (this.product_by_id) {
                var self = this;
                var already_downloaded_products = _.filter(products, function(p){
                    return self.product_by_id[p.id]
                });
                _.each(already_downloaded_products, function(prod){
                    self.product_by_id[prod.id] = prod;
                    if(prod.barcode){
                        self.product_by_barcode[prod.barcode] = prod;
                    }
                });
            }
            var prod_to_download = _.difference(products, already_downloaded_products);
            if (prod_to_download && prod_to_download.length) {
                this._super(prod_to_download);
            }
        },
    });

});
