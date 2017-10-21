odoo.define('pos_mobile.chrome', function (require) {
    "use strict";
    if (!odoo.is_mobile)
        return;

    var screens = require('pos_mobile.screens');
    var chrome = require('point_of_sale.chrome');

    chrome.Chrome.include({
        init: function() {
            this._super();
            this.pos.ready.done(function(){
                var categories = $('.rightpane .categories');
                categories.detach();
                $('.slide-categories').append(categories);
            });
        },
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
        },
    });

    chrome.OrderSelectorWidget.include({
        order_click_handler: function(event,$el) {
            this._super(event,$el);
            var order = this.get_order_by_uid($el.data('uid'));
            if (order) {
                this.chrome.swiperH[0].slideTo(0, 0);
            }
        },
        neworder_click_handler: function(event, $el) {
            this._super(event,$el);
            this.chrome.swiperH[0].slideTo(0, 0);
        },
        deleteorder_click_handler: function(event, $el) {
            this._super(event,$el);
            this.chrome.swiperH[0].slideTo(0, 0);
        },
    });
    return chrome;
});
