odoo.define('vendor_extra_price.import', function (require) {
"use strict";

var core = require('web.core');
var QWeb = core.qweb;
var BaseImport = require('base_import.import');


BaseImport.DataImport.include({
    start: function () {
        var self = this;
        if (this.res_model === 'product.template') {
            this.product_import = {};
            this.fetch_vendors().then(function (result) {
                _.extend(self.product_import, {vendors: result});
            });
            // this.fetch_pricelists().then(function (result) {
            //     _.extend(self.product_import, {pricelists: result});
            // });
        }
        return this._super();
    },

    import_options: function () {
        var self = this;
        var options = {};
        if (this.res_model === 'product.template') {
            var vendor_id = parseInt(this.$('#vendor-select').val());
            if (vendor_id) {
                options.vendor_id = vendor_id;
            }
            var pricelist_id = parseInt(this.$('#pricelist-select').val());
            if (pricelist_id) {
                options.pricelist_id = parseInt(pricelist_id);
            }
        }
        return _.extend(this._super(), options);
    },
    onpreview_success: function (event, from, to, result) {
        var self = this;
        var res = this._super(event, from, to, result);
        if (this.res_model === 'product.template') {
            this.$('.oe_import_box').after($(
                QWeb.render('ProductImportView', this.product_import)));
        }
        return res;
    },

    fetch_vendors: function () {
        return this._rpc({
                model: 'res.partner',
                method: 'search_read',
                args: [[], ['id', 'name']],
                kwargs : {},
            });
    },

    fetch_pricelists: function () {
        return this._rpc({
                model: 'product.pricelist',
                method: 'search_read',
                args: [[], ['id', 'name']],
                kwargs : {},
            });
    },

});

});
