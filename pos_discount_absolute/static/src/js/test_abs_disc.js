odoo.define('pos_discount_absolute.tour', function (require) {
    "use strict";

    var tour = require("web_tour.tour");

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

    tour.register('pos_abs_discount_tour', { test: true, url: '/pos/web' }, steps);

});
