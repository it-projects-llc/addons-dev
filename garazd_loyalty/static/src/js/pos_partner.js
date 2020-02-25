odoo.define('garazd_loyalty.pos_partner', function(require){
    "use strict";

    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.gui');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;


    models.load_fields('res.partner',['loyalty_id', 'loyalty_discount', 'not_apply_loyalty']);
    models.load_fields('res.company',['amount_for_card']);
    models.load_fields('pos.config',['loyalty_card_offer']);
    models.load_fields('product.product', ['standard_price', 'vendor_id']);


    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attributes, options){
            this.discount = 0;
            _super_orderline.initialize.apply(this, arguments);
        },
        get_pricelist_item: function (product_tmpl_id) {
            var domain = [
                ['product_tmpl_id','=',product_tmpl_id],
                ['pricelist_id','=',this.pos.default_pricelist.id],
            ];
            return rpc.query({
                model: 'product.pricelist.item',
                method: 'search_read',
                args: [domain],
            });
        },
        set_discount: function(discount){
            var self = this;
            var order = this.order;
            var partner;
            var new_discount = discount;


            var domain = [
                '|',
                ['product_tmpl_id','=',self.product.product_tmpl_id],
                ['product_id','=',self.product.id],
                ['pricelist_id','=',self.pos.default_pricelist.id],
            ];
            return rpc.query({
                model: 'product.pricelist.item',
                method: 'search_read',
                args: [domain],
            }).then(function(items) {


                var item = null;
                if (items instanceof Array && items.length) {
                    item = items[0];
                }


                if(order !== null){
                    partner = order.get_client();
                }

                if(partner && partner.loyalty_discount) {
                    var product = self.product;
                    if(!item &&
                        (!product.vendor_id ||
                            (product.vendor_id &&
                                !self.pos.db.get_partner_by_id(product.vendor_id[0]).not_apply_loyalty
                            )
                        )
                    ) {
                        new_discount = Math.min(Math.max(parseFloat(partner.loyalty_discount) || 0, 0),100);
                        // if (product.vendor_id && !product.vendor_id.not_apply_loyalty) {
                        //     var extra = (product.list_price - (product.standard_price || 0)) * 100 / product.list_price;
                        //     if (new_discount >= extra) {
                        //         new_discount = 0;
                        //     }
                        // }
                    } else { // Skip if Product has special price in default pricelist
                        new_discount = 0;
                    }
                }

                var disc = Math.min(
                    Math.max(
                        parseFloat(new_discount) || 0,
                        0
                    ),
                    100
                );
                self.discount = disc;
                self.discountStr = '' + disc;
                self.trigger('change',self);

            });
        },
    });


    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({

        initialize: function (session, attributes) {
            this.card_offered = false;
            return _super_order.initialize.apply(this, arguments);
        },

        set_client: function(client){
            _super_order.set_client.apply(this, arguments);
            this.card_offered = false;
            var disc = 0.0;
            if(client && client.loyalty_discount){
                disc = client.loyalty_discount;
            }
            this.get_orderlines().forEach(function(line){
                line.set_discount(disc);
            });
        },

        add_product: function(product, options){
            _super_order.add_product.apply(this, arguments);
            var line = this.get_last_orderline();
            var partner = this.get_client();
            if(partner && partner.loyalty_discount){
                var discount = partner.loyalty_discount;
                if(discount !== undefined){
                    line.set_discount(discount);
                }
            }
        },

        get_total_with_tax: function() {
            var total = _super_order.get_total_with_tax.apply(this, arguments);
            var client = this.get_client();
            var amount_for_card = this.pos.company.amount_for_card;
            if(this.pos.config.loyalty_card_offer == true && this.pos.gui.get_current_screen()) {
                if(amount_for_card > 0.0 && total >= amount_for_card && this.card_offered === false && (!client || client && !client.barcode)) {
                    this.card_offered = true;
                    this.pos.gui.show_popup('alert',{
                        'title': _t('Minimal Purchases Amount'),
                        'body': _t('Offer the client a discount card.'),
                    });
                }
            }
            return total;
        },

    });

    return models;

});
