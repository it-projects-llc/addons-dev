/* Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */

odoo.define('pos_receipt_custom.models', function(require){

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var Qweb = core.qweb;

    models.load_models({
        model: 'pos.custom_receipt',
        fields: ['name','qweb_template', 'type'],
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
            if (table && !this.order_to_transfer_to_different_table) {
                var orders = this.get_order_list();
                if (!orders.length) {
                    // set opening datetime for table
                    table.open_time = this.get_current_datetime();
                }
            }
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

            var hours   = '' + d.getHours();
                hours   = hours.length < 2 ? ('0' + hours) : hours;

            var minutes = '' + d.getMinutes();
                minutes = minutes.length < 2 ? ('0' + minutes) : minutes;

            return {'date': year + '.' + month + '.' + date, 'time': hours + ':' + minutes}
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        custom_qweb_render: function(template, options) {
            var code = Qweb.compile(template), tcompiled;
            var template_name = $(template).attr('t-name');
            try {
                tcompiled = new Function(['dict'], code);
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
            return this.pos.custom_receipt_templates.find(function(receipt){
                return receipt.id === id && receipt.type === type;
            });
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
