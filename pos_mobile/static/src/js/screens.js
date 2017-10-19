odoo.define('pos_mobile.screens', function (require) {
    "use strict";
    if (!odoo.is_mobile)
        return;

    var screens = require('point_of_sale.screens');
    var chrome = require('point_of_sale.chrome');

    chrome.Chrome.include({
        // This method instantiates all the screens, widgets, etc.
        build_widgets: function() {
            this._super();

            $('.pos').addClass('mobile');
                this.swiperH = new Swiper('.swiper-container-h', {
                  spaceBetween: 0,
                  pagination: {
                    el: '.swiper-pagination-h',
                    clickable: true,
                  },
                });
                this.swiperV = new Swiper('.swiper-container-v', {
                  direction: 'vertical',
                  slidesPerView: 'auto',
                  spaceBetween: 0,
                  pagination: {
                    el: '.swiper-pagination-v',
                    clickable: true,
                  },
                });

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

//                var payment = $('.payment-screen');
//                payment.detach();
//                $('.slide-payment').append(payment);

                var categories = $('.rightpane .categories');
                categories.detach();
                $('.slide-categories').append(categories);

//                var clientlist = $('.clientlist-screen');
//                clientlist.detach();
//                $('.slide-clientlist').append(clientlist);
//
//                var receipt = $('.receipt-screen');
//                receipt.detach();
//                $('.slide-receipt').append(receipt);
//
//                var scale = $('.scale-screen');
//                scale.detach();
//                $('.slide-scale').append(scale);

        },

////            $('.pos').addClass('mobile');
////            this.swiper = new Swiper('.swiper-container');
////            var elements = $(".swiper-slide");
////            var width = elements.css('width');
////                width = Number(width.split("px")[0]);
////
////                var screen_width = elements.length * width;
////
////                $('.pos .swiper-wrapper').css({'width': screen_width + 'px'});
////
////                var rightpane = $(".rightpane tbody");
////                var tr = rightpane.find(".header-row");
////                tr.detach();
////                rightpane.append(tr);


    });

//    screens.ProductCategoriesWidget.include({
//        init: function(parent, options){
//            this._super(parent,options);
//            var self = this;
//            this.show_category_list = true;
//            this.show_order_action_buttons = true;
//            $('.breadcrumbs').css({display: 'none'});
//            this.click_category_display = function(event){
//                self.change_display_category_list();
//            };
//            this.click_action_order_display = function(event){
//                self.change_action_buttons();
//            };
//            this.click_order_mobile_screen = function(event){
//                self.change_order_screen();
//            };
//        },
//        change_display_category_list: function(){
//            if (this.show_category_list) {
//                $( '.pos.mobile .categories' ).slideDown();
//                this.show_category_list = false;
//            } else {
//                $( '.pos.mobile .categories' ).slideUp();
//                this.show_category_list = true;
//            }
//        },
//        change_action_buttons: function(){
//            if (this.show_order_action_buttons) {
//                $( '.pos.mobile .pads' ).slideDown();
//                this.show_order_action_buttons = false;
//                $('.fa-plus-square-o').css('display','none');
//                $('.fa-minus-square-o').css('display','inline-block');
//            } else {
//                $( '.pos.mobile .pads' ).slideUp();
//                $('.fa-minus-square-o').css('display','none');
//                $('.fa-plus-square-o').css('display','inline-block');
//                this.show_order_action_buttons = true;
//            }
//        },
//        change_order_screen: function() {
//            var slider = this.pos.swiper;
//            if (slider.activeIndex === 0) {
//                slider.slideNext();
//            } else {
//                slider.slidePrev();
//            }
//        },
//        renderElement: function(){
//            var self = this;
//            this._super.apply(this, arguments);
//            var category_display_button = this.el;
//            var category_button = this.el.querySelector('.category-list-button');
//            category_button.addEventListener('click', this.click_category_display);
//            var action_button = this.el.querySelector('.order-action-buttons');
//            action_button.addEventListener('click', this.click_action_order_display);
//            $('.mobile-order-screen').click(function() {
//                self.change_order_screen();
//            });
//            this.change_display_category_list();
//            this.show_order_action_buttons = !this.show_order_action_buttons;
//            this.change_action_buttons();
//            this.change_breadcrumbs_button();
//        },
//        set_category: function(category){
//            this.show_category_list = false;
//            this._super(category);
//        },
//        change_breadcrumbs_button: function() {
//            if (this.breadcrumb && this.breadcrumb.length) {
//                $('.breadcrumbs').toggle( "slide" );
//            }
//        },
//    });
//
    screens.ProductScreenWidget.include({
        click_product: function(product) {
            this._super.apply(this, arguments);
            var $p = $('span[data-product-id="'+product.id+'"]');
            $($p).animate({
                'opacity': 0.5,
            }, 200, function(){ $($p).animate({
                'opacity': 1,
            }, 400) } );
            var $pi = $('span[data-product-id="'+product.id+'"] img');
            $($pi).animate({
                'max-height': '120px',
                'min-width': '100px',
            }, 200, function(){ $($pi).animate({
                'max-height': '100px',
                'min-width': '60px',
            }, 400) } );
        },
    });
    return screens;
});
