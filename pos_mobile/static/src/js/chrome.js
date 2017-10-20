odoo.define('pos_mobile.chrome', function (require) {
    "use strict";
    if (!odoo.is_mobile)
        return;

    var screens = require('pos_mobile.screens');
    var chrome = require('point_of_sale.chrome');

    chrome.Chrome.include({
        // This method instantiates all the screens, widgets, etc.
        build_widgets: function() {
            this._super();

            $('.pos').addClass('mobile');

            // horizontal swiper
            this.swiperH = new Swiper('.swiper-container-h', {
                spaceBetween: 0,
                pagination: {
                    el: '.swiper-pagination-h',
                    clickable: true,
                },
            });

            // vertical swiper
            this.swiperV = new Swiper('.swiper-container-v', {
                direction: 'vertical',
                slidesPerView: 'auto',
                spaceBetween: 0,
                pagination: {
                    el: '.swiper-pagination-v',
                    clickable: true,
                },
            });

            // move some widgets and screens from screen block to slide blocks
            var products = $('.rightpane .content-row');
            products.detach();
            $(".slide-products").append(products);

            var order = $('.leftpane .order-container');
            order.detach();
            $('.slide-order').append(order);

            var pads = $('.leftpane .pads');
            pads.detach();
            $('.slide-numpad').append(pads);

            var search = $('.rightpane-header');
            search.detach();
            $('.slide-search').append(search);

            var categories = $('.rightpane .categories');
            categories.detach();
            $('.slide-categories').append(categories);

            /* var payment = $('.payment-screen');
            payment.detach();
            $('.slide-payment').append(payment);

            var clientlist = $('.clientlist-screen');
            clientlist.detach();
            $('.slide-clientlist').append(clientlist);

            var receipt = $('.receipt-screen');
            receipt.detach();
            $('.slide-receipt').append(receipt);

            var scale = $('.scale-screen');
            scale.detach();
            $('.slide-scale').append(scale); */

        },
    });

    return chrome;
});
