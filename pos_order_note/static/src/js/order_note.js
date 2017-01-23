odoo.define('pos_cancel_order.order_note', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var multiprint = require('pos_restaurant.multiprint');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var QWeb = core.qweb;
    var _t = core._t;

    models.load_models({
        model:  'product.template',
        fields: ['pos_notes','product_variant_id'],
        loaded: function(self,products){
            products.forEach(function(item){
                if (item.product_variant_id) {
                    var product  = self.db.get_product_by_id(item.product_variant_id[0]);
                    if (product) {
                        product.note = item.pos_notes;
                    }
                }
            });
        }
    });
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options){
            _super_orderline.initialize.apply(this,arguments);
            if (this.product.note) {
                this.set_note(this.product.note);
            }
        },
    });
});
