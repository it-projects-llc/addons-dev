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

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
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
            if (printer.config.receipt_format_id && (changes['new'].length > 0 || changes['cancelled'].length > 0)) {
                var receipt_template = this.get_receipt_template_by_id(printer.config.receipt_format_id[0]);
                var template = $.parseXML(receipt_template.qweb_template).children[0];
                var receipt = this.render_custom_qweb(template, {changes:changes, widget:this});
                printer.print(receipt);
            } else {
                _super_order.print_order_receipt.apply(this,arguments);
            }
        },
    });
});
