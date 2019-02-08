odoo.define('alan_customize.front_js_multi',function(require){
    'use strict';
    
    var sAnimation = require('website.content.snippets.animation');
    function initialize_owl(el){
        el.owlCarousel({
        items: 4,
            margin: 25,
            navigation: true,
            pagination: false,
            responsive: {
                0: {
                    items: 1,
                },
                481: {
                    items: 2,
                },
                768: {
                    items: 3,
                },
                1024: {
                    items: 4,
                }
            }

        });
    }
    
    function destory_owl(el){
        if(el && el.data('owlCarousel')){
            el.data('owlCarousel').destroy();
            el.find('.owl-stage-outer').children().unwrap();
            el.removeData();
        }
    }

    sAnimation.registry.s_product_multi_with_header = sAnimation.Class.extend({
        selector : ".js_multi_collection",
        start: function (editMode) {
            var self = this;
            if (self.editableMode){
                self.$target.empty().append('<div class="container"><div class="product_slide" contentEditable="false"><div class="col-md-12"><div class="seaction-head"<h1>Multitab Product with Header</h1></div></div></div></div>');
            }
            if(!self.editableMode){
                var list_id=self.$target.attr('data-list-id') || false;
                $.get("/shop/get_multi_tab_content",{'collection_id':list_id}).then(function (data){
                    if(data){
                        self.$target.empty().append(data);
                        $(".js_multi_collection").removeClass('hidden');
                        $('a[data-toggle="tab"]').on('shown.bs.tab', function () {
                            initialize_owl($(".multi_tab_slider .tab-content .active .multi_slider"));
                        }).on('hide.bs.tab', function () {
                            destory_owl($(".multi_tab_slider .tab-content .active .multi_slider"));
                        });
                        initialize_owl($(".multi_tab_slider .tab-content .active .multi_slider"));
                    }
                });
            }
        },
    });

    sAnimation.registry.s_product_multi_snippet = sAnimation.Class.extend({
        selector : ".multi_tab_product_snippet",
        start: function (editMode) {
            var self = this;
            self.$target.empty();
            if (self.editableMode){
                self.$target.empty().append('<div class="container"><div class="product_slide" contentEditable="false"><div class="col-md-12"><div class="seaction-head"<h1>Multitab Product with Header</h1></div></div></div></div>');
            }
            if(!self.editableMode){
                var list_id=self.$target.attr('data-list-id') || false;
                $.get("/shop/multi_tab_product_snippet",{'collection_id':list_id}).then(function (data){
                    if(data){
                        self.$target.empty().append(data);
                        $(".multi_tab_product_snippet").removeClass('hidden');
                        }
                });
            }
        },
    });

    $(document).ready(function() {
        $('.multi_tab_slider li a[data-toggle="tab"]').on('shown.bs.tab', function () {
            $(".multi_slider").owlCarousel({
                items: 4,
                margin: 25,
                navigation: true,
                pagination: false,
                responsive: {
                    0: {
                        items: 1,
                    },
                    481: {
                        items: 2,
                    },
                    768: {
                        items: 3,
                    },
                    1024: {
                        items: 4,
                    }
                }
            });
        });
    });
});

