odoo.define('pos_mobile.screens', function (require) {
    "use strict";
    if (!odoo.is_mobile)
        return;

    var screens = require('point_of_sale.screens');
    var models = require('pos_mobile.models');

    screens.ProductCategoriesWidget.include({
        init: function(parent, options){
            this._super(parent,options);
            var self = this;
            this.click_categories_slide = function(event){
                self.change_categories_slide();
            };
            this.click_numpad_slide = function(event){
                self.change_numpad_slide();
            };
            this.click_order_slide = function(event){
                self.change_order_slide();
            };
            this.switch_category_handler = function(event){
                self.set_category(self.pos.db.get_category_by_id(Number(this.dataset.categoryId)));
                self.renderElement();
                self.chrome.swiperH[0].slideTo(1);
            };
        },
        open_bottom_menu: function() {
            var slider = this.chrome.swiperV;
            slider.slideNext();
            $('.order-swiper').addClass('swipe-is-open');
        },
        close_bottom_menu: function() {
            var slider = this.chrome.swiperV;
            slider.slidePrev();
            this.current_bottom_slide = false;
            $('.order-swiper').removeClass('swipe-is-open');
            $('.order-swiper').removeClass('open-categories-slide');
            $('.order-swiper').removeClass('open-numpad-slide');
        },
        // second horizontal swiper contain categories, numpad and buttons slides
        change_categories_slide: function() {
            if (this.current_bottom_slide === "categories") {
                this.close_bottom_menu();
            } else {
                this.open_bottom_menu();
                // go to first slide
                var slider = this.chrome.swiperH[1];
                slider.slideTo(0);

                this.current_bottom_slide = "categories";
                $('.order-swiper').removeClass('open-numpad-slide');
                $('.order-swiper').addClass('open-categories-slide');
            }
        },
        change_numpad_slide: function() {
            if (this.current_bottom_slide === "numpad") {
                this.close_bottom_menu();
            } else {
                this.open_bottom_menu();
                // go to second slide
                var slider = this.chrome.swiperH[1];
                slider.slideTo(1);
                this.current_bottom_slide = "numpad";
                $('.order-swiper').removeClass('open-categories-slide');
                $('.order-swiper').addClass('open-numpad-slide');
            }
        },
        // first horizontal swiper contain order and products slides
        change_order_slide: function() {
            var slider = this.chrome.swiperH[0];
            if (slider.activeIndex === 0) {
                slider.slideNext();
            } else {
                slider.slidePrev();
            }
        },
        renderElement: function(){
            var self = this;
            this._super.apply(this, arguments);
            // adds event for buttons in search panel
            this.el.querySelector('.slide-categories-button').addEventListener('click', this.click_categories_slide);
            this.el.querySelector('.slide-numpad-button').addEventListener('click', this.click_numpad_slide);
            this.el.querySelector('.slide-order-button').addEventListener('click', this.click_order_slide);
        },
        perform_search: function(category, query, buy_result){
            this._super.apply(this, arguments);
            if (query) {
                this.chrome.swiperH[0].slideTo(1);
            }
        },
        clear_search: function(){
            this._super();
            var parent = $(".pos.mobile .swiper-container .rightpane-header")[0];
            var input = parent.querySelector('.searchbox input');
                input.value = '';
                input.focus();
        },
    });

    screens.ProductScreenWidget.include({
        click_product: function(product) {
            this._super.apply(this, arguments);
            // adds click effect
            if ($('.product-count')) {
                $('.product-count').remove();
            }
            var $p = $('span[data-product-id="'+product.id+'"]');
            $($p).animate({
                'opacity': 0.5,
            }, 200, function(){ $($p).animate({
                'opacity': 1,
            }, 400) } );
            var $pi = $('span[data-product-id="'+product.id+'"] img');
            $($pi).animate({
                'max-height': '240px',
                'min-width': '200px',
            }, 200, function(){
                $($pi).animate({
                    'max-height': '200px',
                    'min-width': '128px',
                }, 400)
            });
            var order = this.pos.get_order();
            var qty = order.get_quantity_by_product_id(product.id);
            $p.append('<span class="product-count">'+qty+'</span>');
            var count = $($p.children()[2]);
            count.animate({
                'font-size': '150px',
                'top': '-40%',
            }, 400, function(){
                count.remove();
            });
        },
    });

    screens.ClientListScreenWidget.include({
        partner_icon_url: function(id){
            return '/web/image?model=res.partner&id='+id+'&field=image_medium';
        },
    });

    screens.NumpadWidget.include({
        clickAppendNewChar: function(event) {
            var res = this._super(event);
            this.scroll_to_selected_line();
            return res;
        },
        scroll_to_selected_line: function() {
            var order = this.pos.get_order();
            var width = order.get_orderlines().indexOf(order.get_selected_orderline());
            $('.order-scroller').animate({scrollTop:104 * width}, 200, 'swing');
        },
    });
    return screens;
});
