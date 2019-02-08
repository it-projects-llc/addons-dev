$(document).ready(function() {
    odoo.define('alan_customize.wishlist',function(require){
        'use strict';
        var ajax = require('web.ajax');
        var website_sale_utils = require('website_sale.utils');
        $('.o_add_wishlist_dyn').click(function (e){
            e.preventDefault();
            e.stopPropagation();
            var product_id = $(e.currentTarget).data('product-product-id');
            return ajax.jsonRpc('/shop/wishlist/add', 'call', {
                'product_id': product_id
            }).then(function () {
                website_sale_utils.animate_clone($('#my_wish'), $(e.currentTarget).closest('form'), 25, 40);
                $(e.currentTarget).prop("disabled", true).addClass('disabled');
            });
        });
        var website_sale_utils = require('website_sale.utils');
        $('.o_add_wishlist').click(function (e){
        e.preventDefault();
        e.stopPropagation();
            var product_id = $(e.currentTarget).data('product-product-id');
            return ajax.jsonRpc('/shop/wishlist/add', 'call', {
                'product_id': product_id
            }).then(function () {
                website_sale_utils.animate_clone($('#my_wish'), $(e.currentTarget).closest('form'), 25, 40);
                $(e.currentTarget).prop("disabled", true).addClass('disabled');
            });
        });
    });
});
