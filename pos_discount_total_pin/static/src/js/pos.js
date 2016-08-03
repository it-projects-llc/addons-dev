odoo.define('pos_discount_total_pin.pos', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    require('pos_discount_total.OrderWidget');
    var core = require('web.core');
    var _t = core._t;

    screens.PaymentScreenWidget.include({
        validate_order: function(force_validation) {
            var self = this;
            var _super = this._super;
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            var discount = false;
            for (var i = 0; i < orderlines.length; i++) {
                var line = orderlines[i];
                if (line.discount) {
                    discount = true;
                    self.gui.sudo_custom({
                        'title': _t('Insert security PIN:'),
                        'special_group': this.pos.config.discount_total_group_id[0]
                    }).done(function (user) {
                        order.discount_total_user_id = user;
                        _super.call(self, force_validation);
                    });
                    break;
                }
            }
            if (!discount) {
                this._super(force_validation);
            }
        }
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            json.discount_total_user_id = this.discount_total_user_id ? this.discount_total_user_id.id : false;
            return json;
        }
    });
});
