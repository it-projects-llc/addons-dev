/* Copyright 2017-2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_discount_absolute.tour', function (require) {
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

    function add_absolute_discount() {
        return [{
            content: 'open discount widget ',
            trigger: '.js_discount',
        }, {
            content: 'choose absolute discount',
            trigger: '.absolute',
        }, {
            content: 'add value',
            trigger: 'button[data-action="+50"]',
        }, {
            content: 'confirm',
            trigger: '.popup-abs-discount > div.footer.centered > div.button.confirm',
        }];
    }

    function add_relative_discount() {
        return [{
            content: 'open discount widget ',
            trigger: '.js_discount',
        }, {
            content: 'choose absolute discount',
            trigger: '.percentage',
        }, {
            content: 'confirm',
            trigger: '.popup-abs-discount > div.footer.centered > div.button.confirm',
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

    steps = steps.concat(add_product_to_order('Ekomurz.nl'));
    steps = steps.concat(add_absolute_discount());
    steps = steps.concat(add_relative_discount());

    tour.register('pos_abs_discount_tour', { test: true, url: '/web' }, steps);

});
