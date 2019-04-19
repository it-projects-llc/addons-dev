/* Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_receipt_custom_template_beckhoff.models', function(require){

    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var core = require('web.core');

    var _t = core._t;
    var Qweb = core.qweb;

    models.load_fields('product.product', ['product_brand_id']);

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(table) {
            var self = this;
            var pos_receipt_custom_template_model = _.find(this.models, function(model){
                return model.model === 'pos.custom_receipt';
            });
            var old_table = this.table;
            var super_domain = _.bind(pos_receipt_custom_template_model.domain, self);
            pos_receipt_custom_template_model.domain = function(it) {
                var domain = super_domain(it);
                if (it.config.custom_invoice_receipt) {
                    domain[0][2].push('receipt');
                }
                return domain;
            };
            var super_condition = _.bind(pos_receipt_custom_template_model.condition, self);
            pos_receipt_custom_template_model.condition = function(it) {
                return super_condition(it) || it.config.custom_invoice_receipt;
            };
            return _super_posmodel.initialize.apply(this, arguments);
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        //used to create a json of the ticket, to be sent to the printer
        export_for_printing: function(){
            var res = _super_orderline.export_for_printing.apply(this, arguments);
            var prod = this.get_product();
            res.brand_name = prod.product_brand_id && prod.product_brand_id[1];
            res.categ_name = prod.categ_id && prod.categ_id[1];
            return res;
        },
    });

    return models;

});
