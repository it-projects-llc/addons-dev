/* Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_receipt_custom_template.screens', function(require){

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');

    gui.Gui.prototype.screen_classes.filter(function(el) {
        return el.name === 'invoice_receipt';
    })[0].widget.include({
        render_invoice_receipt: function(){

            if (this.pos.config.custom_invoice_receipt) {
                var order = this.pos.get_order();
                var receipt_template = order.get_receipt_template_by_id(this.pos.config.custom_invoice_receipt_id[0], 'receipt');
                var printing_data = order.export_for_printing();
                var header_image = receipt_template.printable_image
                ? 'data:image/png;base64,' + receipt_template.printable_image
                : printing_data.company.logo;
                var template = $.parseXML(receipt_template.qweb_template).children[0];
                var receipt = order.custom_qweb_render(template, {
                    widget: this,
                    order: order,
                    header_image: header_image,
                    receipt: printing_data,
                    orderlines: order.get_orderlines(),
                    paymentlines: order.get_paymentlines(),
                    display_time: this.get_display_time() || false,
                });
                if (this.save_order_receipt) {
                    $(template).find(".receipt-type").html("(Supplement)");
                    this.save_order_receipt(order, template.outerHTML, 'ticket');
                }
                return receipt;
            }

            return this._super();
        },
    });

    return screens;
});
