odoo.define('pos_mobile.screens', function (require) {
    "use strict";
    if (!odoo.is_mobile)
        return;

    var screens = require('point_of_sale.screens');

    screens.ProductCategoriesWidget.include({
        init: function(parent, options){
            this._super(parent,options);
            var self = this;
            this.show_category_list = true;
            this.show_order_action_buttons = true;
            this.change_category_display = function(event){
                if (self.show_category_list) {
                    $( '.pos.mobile .categories' ).slideDown();
                    self.show_category_list = false;
                } else {
                    $( '.pos.mobile .categories' ).slideUp();
                    self.show_category_list = true;
                }
            };
            this.change_action_order_buttons_display = function(event){
                if (self.show_order_action_buttons) {
                    $( '.pos.mobile .pads' ).slideDown();
                    self.show_order_action_buttons = false;
                    $('.fa-plus-square-o').css('display','none');
                    $('.fa-minus-square-o').css('display','inline-block');
                } else {
                    $( '.pos.mobile .pads' ).slideUp();
                    $('.fa-minus-square-o').css('display','none');
                    $('.fa-plus-square-o').css('display','inline-block');
                    self.show_order_action_buttons = true;
                }
            };
        },
        renderElement: function(){
            this._super.apply(this, arguments);
            var category_display_button = this.el;
            var category_button = this.el.querySelector('.category-list-button');
            category_button.addEventListener('click', this.change_category_display);
            var action_button = this.el.querySelector('.order-action-buttons');
            action_button.addEventListener('click', this.change_action_order_buttons_display);
        },
    });

    screens.ProductScreenWidget.include({
        renderElement: function () {
            this._super.apply(this, arguments);
            var self = this;
            this.pos.ready.then(function(){
                $('.pos').addClass('mobile');
                var swiper = new Swiper('.swiper-container');
                var elements = $(".swiper-slide");
                var width = elements.css('width');
                width = Number(width.split("px")[0]);

                var screen_width = elements.length * width;

                $('.pos .swiper-wrapper').css({'width': screen_width + 'px'});

                var rightpane = $(".rightpane tbody");
                var tr = rightpane.find(".header-row");
                tr.detach();
                rightpane.append(tr);
            });
        },
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
