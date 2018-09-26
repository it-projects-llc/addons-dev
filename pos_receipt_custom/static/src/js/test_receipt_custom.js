/* Copyright 2017-2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_receipt_custom.tour', function (require) {
    "use strict";

    var core = require('web.core');
    var tour = require('web_tour.tour');

    var _t = core._t;

    function add_product_to_order(product_name) {
        return [{
            content: 'buy ' + product_name,
            trigger: '.product-list .product-name:contains("' + product_name + '")',
        }, {
            content: 'the ' + product_name + ' have been added to the order',
            trigger: '.order .product-name:contains("' + product_name + '")',
        }];
    }

    function payment(pay_method) {
        return [{
            trigger: '.button.pay',
            content: _t("Open the payment screen"),
        }, {
            content: "Choose Administrator like a cashier or make a dummy action",
            trigger: '.modal-dialog.cashier:not(.oe_hidden) .cashier .selection-item:contains("Administrator"), .payment-screen:not(.oe_hidden) h1:contains("Payment")'
        }, {
            extra_trigger: '.button.paymentmethod:contains("' + pay_method +'")',
            trigger: '.button.paymentmethod:contains("' + pay_method +'")',
            content: _t("Click the payment method"),
        }, {
            trigger: '.payment-screen:not(".oe_hidden") .numpad button[data-action="9"]',
            content: 'Set payment amount',
        }, {
            extra_trigger: '.button.next.highlight:contains("Validate")',
            trigger: '.button.next.highlight:contains("Validate")',
            content: 'Validate payment',
        }];
    }

    function check_receipt() {
        return [{
            extra_trigger: '.receipt-screen:not(".oe_hidden") .pos-receipt-container',
            trigger: '.receipt-type:contains("(Receipt)")',
            content: 'Validate payment',
        }, {
            extra_trigger: '.pos-sale-ticket',
            trigger: '.button.next.highlight:contains("Next Order")',
            content: 'Check proceeded validation',
        }];
    }

    var steps = [{
            trigger: '.o_app[data-menu-xmlid="point_of_sale.menu_point_root"], .oe_menu_toggler[data-menu-xmlid="point_of_sale.menu_point_root"]',
            content: _t("Ready to launch your <b>point of sale</b>? <i>Click here</i>."),
            position: 'bottom',
        }, {
            trigger: ".o_pos_kanban button.oe_kanban_action_button",
            content: _t("<p>Click to start the point of sale interface. It <b>runs on tablets</b>, laptops, or industrial hardware.</p><p>Once the session launched, the system continues to run without an internet connection.</p>"),
            position: "bottom"
        },{
            content: "Switch to table or make dummy action",
            trigger: '.table:not(.oe_invisible .neworder-button), .order-button.selected',
            position: "bottom"
        },{
            content: 'waiting for loading to finish',
            trigger: '.neworder-button > .fa-plus',
        }];

    steps = steps.concat(add_product_to_order('Carrots'));
    steps = steps.concat(payment('Cash'));
    steps = steps.concat(check_receipt());

    tour.register('pos_receipt_custom_tour', { test: true, url: '/web' }, steps);

});
