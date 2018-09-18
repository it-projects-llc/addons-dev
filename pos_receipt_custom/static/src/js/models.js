/*  Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
    Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_receipt_custom.models', function(require){

    var models = require('point_of_sale.models');
    var core = require('web.core');

    var _t = core._t;
    var Qweb = core.qweb;

    models.load_models({
        model: 'pos.custom_receipt',
        fields: ['name','qweb_template', 'type', 'printable_image'],
        loaded: function(self, templates) {
            self.custom_receipt_templates = templates;
        },
    });

    models.load_fields('product.product', ['second_product_name']);
    models.load_fields('res.company', ['street', 'city']);

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        // changes the current table.
        set_table: function(table) {
            var old_table = this.table;
            if (table && !this.order_to_transfer_to_different_table) {
                this.table = table;
                var orders = this.get_order_list();
                if (!orders.length) {
                    // set opening datetime for table
                    table.open_time = this.get_current_datetime();
                }
            }
            this.table = old_table;
            _super_posmodel.set_table.apply(this, arguments);
        },
        get_current_datetime: function(){
            var d = new Date();

            var date = d.getDate();
            //January is 0
            var month = d.getMonth() + 1;
            var year = d.getFullYear();

            if (date < 10) {
                date = '0' + date;
            }

            if (month < 10) {
                month = '0' + month;
            }

            var hours = '' + String(d.getHours());
                hours = hours.length < 2
                ? ('0' + hours)
                : hours;

            var minutes = '' + String(d.getMinutes());
                minutes = minutes.length < 2
                ? ('0' + minutes)
                : minutes;

            return {'date': year + '.' + month + '.' + date, 'time': hours + ':' + minutes};
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        custom_qweb_render: function(template, options) {
            var code = Qweb.compile(template), tcompiled;
            var template_name = $(template).attr('t-name');
            try {
                tcompiled = eval("new Function(['dict'], code);");
            } catch (error) {
                Qweb.tools.exception("Error evaluating template: " + error, { template: template_name });
            }
            if (!tcompiled) {
                Qweb.tools.exception("Error evaluating template: (IE?)" + error, { template: template_name });
            }
            Qweb.compiled_templates[template_name] = tcompiled;
            return Qweb.render(template_name, options);
        },
        get_receipt_template_by_id: function(id, type) {
            return _.find(this.pos.custom_receipt_templates, function(receipt){
                return receipt.id === id && receipt.type === type;
            });
        },
        get_last_orderline_user_name: function(){
            var lastorderline = this.get_last_orderline();
            var name = this.pos.get_cashier().name;
            if (lastorderline && lastorderline.ms_info) {
                name = lastorderline.ms_info.created.user.name;
            }
            return name;
        },
        get_receipt_type: function(type){
            return this.receipt_type || _t("Receipt");
        },
        set_receipt_type: function(type) {
            this.receipt_type = type;
        },
        get_total_order_discount: function() {
            var self = this;
            var sum = this.get_total_discount();

            var disc_product_id = this.pos.config.discount_product_id && this.pos.config.discount_product_id[0];
            // compatibility with pos_discount and pos_discount_absolute
            if (disc_product_id) {
                sum -= this.get_discount_product_display_price(disc_product_id);

                var abs_disc_product_id = this.pos.config.discount_abs_product_id && this.pos.config.discount_abs_product_id[0];
                if (abs_disc_product_id) {
                    sum -= this.get_discount_product_display_price(abs_disc_product_id);
                }
            }
            return sum;
        },
        get_discount_product_display_price: function(disc_product_id) {
            var disc_product = this.pos.db.get_product_by_id(disc_product_id);
            disc_product = _.find(this.get_orderlines(), function(pl) {
                return pl.product.id === disc_product_id;
            });
            return disc_product
            ? disc_product.get_display_price()
            : 0;
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        //used to create a json of the ticket, to be sent to the printer
        export_for_printing: function(){
            var res = _super_orderline.export_for_printing.apply(this, arguments);
            res.second_product_name = this.get_product().second_product_name;
            return res;
        },
    });

    return models;
});
