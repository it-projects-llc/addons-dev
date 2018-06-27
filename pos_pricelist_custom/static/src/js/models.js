odoo.define('pos_pricelist_custom.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        get_pricelist_by_id: function(id) {
            return this.pricelists.find(function(pricelist) {
                return pricelist.id === id;
            });
        }
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        set_pricelist: function (pricelist) {
            var lines_to_recompute = _.filter(this.get_orderlines(), function (line) {
                return ! line.price_manually_set;
            });
            _.each(lines_to_recompute, function (line) {
                line.pricelist = pricelist;
            });
            _super_order.set_pricelist.apply(this, arguments);
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options) {
            this.pricelist = {};
            _super_orderline.initialize.apply(this, arguments);
        },
        set_default_pricelist: function() {
            var pricelist = this.pos.default_pricelist;
            var order = this.pos.get_order();
            this.set_unit_price(this.product.get_price(pricelist, this.get_quantity()));
            order.fix_tax_included_price(this);
            this.pricelist = pricelist;
            this.trigger('change', this);
        },
        init_from_JSON: function(json) {
            _super_orderline.init_from_JSON.apply(this, arguments);
            this.pricelist = json.pricelist;
        },
        export_as_JSON:function(){
            var res = _super_orderline.export_as_JSON.apply(this, arguments);
            res.pricelist = this.pricelist;
            return res;
        },
    });

    return models;
});
