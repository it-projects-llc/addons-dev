odoo.define('pos_order_receipt_custom', function (require) {
    "use strict";

    var models = require('pos_restaurant_base.models');
    var core = require('web.core');

    var Qweb = core.qweb;

    models.load_models({
        model: 'pos.order_receipt',
        fields: ['qweb_template'],
        loaded: function(self, receipt_formats){
            self.receipt_formats = receipt_formats;
        },
    });

    models.load_fields('restaurant.printer',['receipt_format_id']);

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        // changes the current table.
        set_table: function(table) {
            var self = this;
            if (table && this.order_to_transfer_to_different_table && !this.order_to_transfer_to_different_table.first_order_printing) {
                var old_table = this.order_to_transfer_to_different_table.table;
                var new_table = table;

                // FIXME: table data
                var changes = {
                    'changes_table': {
                        'new_table': new_table,
                        'old_table': old_table,
                    },
                    'new': [],
                    'cancelled': [],
                    'new_all': [],
                    'cancelled_all': [],
                };

                // print transfer info to all printers
                this.printers.forEach(function(printer){
                    self.order_to_transfer_to_different_table.print_order_receipt(printer, changes);
                });
            }
            _super_posmodel.set_table.apply(this, arguments);
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (session, attributes) {
            this.first_order_printing = true;
            return _super_order.initialize.apply(this, arguments);
        },
        get_receipt_template_by_id: function(id) {
            return this.pos.receipt_formats.find(function(receipt){
                return receipt.id === id;
            });
        },
        render_custom_qweb: function(template, options) {
            var code = Qweb.compile(template), tcompiled;
            try {
                tcompiled = new Function(['dict'], code);
            } catch (error) {
                Qweb.tools.exception("Error evaluating template: " + error, { template: name });
            }
            if (!tcompiled) {
                Qweb.tools.exception("Error evaluating template: (IE?)" + error, { template: name });
            }
            var template_name = $(template).attr('t-name')
            Qweb.compiled_templates[template_name] = tcompiled;
            return Qweb.render(template_name, options);
        },
        print_order_receipt: function(printer, changes) {
            if (printer.config.receipt_format_id && (changes['new'].length > 0 || changes['cancelled'].length > 0 || changes.changes_table)) {
                // all order data
                changes.order = this.export_as_JSON();
                changes.waiter = this.pos.get_cashier();

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
                changes.date = {'date': date, 'month': month, 'year':year};
                changes.printer = {'name': printer.config.name};

                var receipt_template = this.get_receipt_template_by_id(printer.config.receipt_format_id[0]);
                var template = $.parseXML(receipt_template.qweb_template).children[0];
                var receipt = this.render_custom_qweb(template, {changes:changes, widget:this});
                printer.print(receipt);
            } else {
                _super_order.print_order_receipt.apply(this,arguments);
            }
            this.first_order_printing = false;
        },
        export_as_JSON: function(){
            var json = _super_order.export_as_JSON.call(this);
            json.first_order_printing = this.first_order_printing;
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.first_order_printing = json.first_order_printing;
        },
    });
});
