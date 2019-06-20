// Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
odoo.define('pos_invoice_number.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var _t = core._t;

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        generate_unique_invoice_id: function() {
            // Generates a public identification number for the order invoice.
            // The generated number must be unique and sequential.
            var uniq_id = this.generate_unique_id().split('-').join('');
            return this.pos.config.invoice_prefix + '-' + uniq_id.substring(uniq_id.length - 9, uniq_id.length);
        },

        generate_unique_invoice_access_key: function() {
            // Generates a access key number for the order invoice.
            var date = new Date();
            // length 4
            var year = '' + date.getFullYear();
            // length 2
            var month = date.getMonth() + 1;
            month = month >= 10
            ? '' + month
            : '0' + month;
            // length 2
            var day = date.getDate();
            day = day >= 10
            ? '' + day
            : '0' + day;
            date = year + month + day;

            var random_number = function(length) {
               var result           = '';
               var characters       = '0123456789';
               var charactersLength = characters.length;
               for ( var i = 0; i < length; i++ ) {
                  result += characters.charAt(Math.floor(Math.random() * charactersLength));
               }
               return result;
            }
            return date + random_number(49 - 8);
        },

        set_to_invoice: function(to_invoice) {
            _super_order.set_to_invoice.apply(this, arguments);
            this.invoice_name = this.generate_unique_invoice_id();
            this.access_key = this.generate_unique_invoice_access_key();
        },

        export_as_JSON: function() {
            var data = _super_order.export_as_JSON.apply(this, arguments);
            var is_to_invoice = this.is_to_invoice();
            if (is_to_invoice) {
                data.invoice_name = this.invoice_name;
                data.access_key = this.access_key;
            }
            // we duplicate this argument because _save_to_server method uses one option parameter `to_invoice` for all orders to save
            data.to_invoice = is_to_invoice;
            return data;
        },

        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this, arguments);
            if (json.to_invoice) {
                this.invoice_name = json.invoice_name;
                this.access_key = json.access_key;
            }
            this.to_invoice = json.to_invoice || false;
        },

    });

    screens.PaymentScreenWidget.include({
        finalize_validation: function() {
            var order = this.pos.get_order();
            if (!order.is_to_invoice()) {
                return this._super();
            }

            var self = this;
            // copy-pasted part from Odoo except one error message

            if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) {

                    this.pos.proxy.open_cashbox();
            }

            order.initialize_validation_date();
            order.finalized = true;

            if (order.is_to_invoice()) {
                var invoiced = this.pos.push_and_invoice_order(order);
                this.invoicing = true;

                invoiced.fail(function(error){
                    order.finalized = false;
                    self.invoicing = false;
                    if (error.message === 'Missing Customer') {
                        self.gui.show_popup('alert',{
                            'title': _t('Please select the Customer'),
                            'body': _t('You need to select the customer before you can invoice an order.'),
                        });
                    } else if (error.message === 'Backend Invoice') {
                        self.gui.show_popup('confirm',{
                            'title': _t('Please print the invoice from the backend'),
                            'body': _t('The order has been synchronized earlier. Please make the invoice from the backend for the order: ') + error.data.order.name,
                            confirm: function () {
                                this.gui.show_screen('receipt');
                            },
                            cancel: function () {
                                this.gui.show_screen('receipt');
                            },
                        });
                    } else if (error.code === 200) {
                        self.gui.show_popup('error-traceback',{
                            'title': error.data.message || _t("Server Error"),
                            'body': error.data.debug || _t('The server encountered an error while receiving your order.'),
                        });
                    } else {
                        /*  self.gui.show_popup('alert',{
                            'title': _t("Network Error"),
                            'body':  _t("The order will be sent when the connection restored"),
                        }); */
                        order.finalized = true;
                        self.gui.show_screen('receipt');
                    }
                });

                invoiced.done(function(){
                    self.invoicing = false;
                    self.gui.show_screen('receipt');
                });
            } else {
                this.pos.push_order(order);
                this.gui.show_screen('receipt');
            }

        },
    });

    return {
        models: models,
        screens: screens,
    };
});
