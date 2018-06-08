/* Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */

odoo.define('pos_receipt_custom', function(require){

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
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

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        //used to create a json of the ticket, to be sent to the printer
        export_for_printing: function(){
            var res = _super_orderline.export_for_printing.apply(this, arguments);
            res.second_product_name = this.get_product().second_product_name;
            return res;
        },
    });

    screens.ReceiptScreenWidget.include({
        custom_qweb_render: function(template, options) {
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
        get_receipt_template_by_id: function(id, type) {
            return this.pos.custom_receipt_templates.find(function(receipt){
                return receipt.id === id && receipt.type === type;
            });
        },
        render_receipt: function(){
            if (this.pos.config.custom_ticket) {

                if (this.pos.table) {
                    var open_time = this.pos.table.open_time;
                    var payment_time = this.pos.get_current_datetime();

                    var display_time = {time: open_time.time + "-" + payment_time.time};

                    if (open_time.date === payment_time.date) {
                        display_time.date = open_time.date;
                    } else {
                        display_time.date = open_time.date + "-" + payment_time.date;
                    }
                }

                var order = this.pos.get_order();
                var ticket_template = this.get_receipt_template_by_id(this.pos.config.custom_ticket_id[0], 'ticket');
                var template = $.parseXML(ticket_template.qweb_template).children[0];
                var ticket = this.custom_qweb_render(template, {
                    widget: this,
                    order: order,
                    receipt: order.export_for_printing(),
                    orderlines: order.get_orderlines(),
                    paymentlines: order.get_paymentlines(),
                    display_time: display_time || false,
                });
                this.$('.pos-receipt-container').html(ticket);
            } else {
                this._super();
            }
        },
        print_xml: function() {
            if (this.pos.config.custom_xml_receipt) {

                if (this.pos.table) {
                    var open_time = this.pos.table.open_time;
                    var payment_time = this.pos.get_current_datetime();

                    var display_time = {time: open_time.time + "-" + payment_time.time};

                    if (open_time.date === payment_time.date) {
                        display_time.date = open_time.date;
                    } else {
                        display_time.date = open_time.date + "-" + payment_time.date;
                    }
                }

                var env = {
                    widget:  this,
                    pos: this.pos,
                    order: this.pos.get_order(),
                    receipt: this.pos.get_order().export_for_printing(),
                    paymentlines: this.pos.get_order().get_paymentlines(),
                    display_time: display_time || false,
                };

                var receipt_template = this.get_receipt_template_by_id(this.pos.config.custom_xml_receipt_id[0], 'receipt');
                var template = $.parseXML(receipt_template.qweb_template).children[0];
                var receipt = this.custom_qweb_render(template, env);
                this.pos.proxy.print_receipt(receipt);
                this.pos.get_order()._printed = true;
            } else {
                this._super();
            }
        },
    });
});
