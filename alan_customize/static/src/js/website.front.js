odoo.define('alan_customize.front_js',function(require){
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
                    items: 2,
                },
                1024: {
                    items: 4,
                },
                1280: {
                    items: 4,
                },
                1600: {
                    items: 5,
                }
            }
        });
    }
    
    function initialize_owl_1(el){
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
                    items: 2,
                },
                1024: {
                    items: 4,
                }
            }
        });
    }

    function initialize_owl_multi(el){
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

    sAnimation.registry.product_brand_slider = sAnimation.Class.extend({
        selector: ".tqt-product-brand-slider",
        start: function(editable_mode) {
            var self = this;
            if (self.editableMode) {
                self.$target.empty().append('<div class="container"><div class="shopper_brand_slider"><div class="col-md-12"><div class="seaction-head"><h1>Brand Slider</h1> </div></div></div></div>');
            }
            if (!self.editableMode) {
                $.get("/shop/get_product_brand_slider", {
                    'label': self.$target.attr('data-brand-label') || '',
                    'brand-count': self.$target.attr('data-brand-count') || 0,
                }).then(function(data) {
                    if (data) {
                        self.$target.empty().append(data);
                        $.getScript("/alan_customize/static/src/js/owl.carousel.min.js");
                        self.$target.find("#as_our_brand").owlCarousel({
                            items: parseInt(self.$target.attr('data-brand-count')) || 8,
                            margin: 10,
                            navigation: true,
                            pagination: false,
                            responsive: {
                                0: {
                                    items: 2,
                                },
                                481: {
                                    items: 3,
                                },
                                768: {
                                    items: 4,
                                },
                                1024: {
                                    items: parseInt(self.$target.attr('data-brand-count')) || 8,
                                }
                            }
                        });
                    }
                });
            }
        }
    });
    
    sAnimation.registry.latest_blog_snippet_s = sAnimation.Class.extend({
        selector : ".as-blog-option-02",
        start: function (editMode) {
            var self = this;
            if (self.editableMode){
                self.$target.empty().append('<div class="container">Latest Blog Snippet 2</div>');
            }
            if(!self.editableMode){
                $.get("/shop/get_latest_blog_snip_content",{}).then(function( data ) {
                    if(data){
                        self.$target.empty().append(data);
                        $(".as-blog-option-02").removeClass('hidden');
                    }
                });
            }
        }
    });
    
    sAnimation.registry.product_slider_actions = sAnimation.Class.extend({
        selector : ".s_product_slider",
        start: function (editMode) {
            var self = this;
            if (self.editableMode){
                self.$target.empty().append('<div class="container"><div class="seaction-head"><h2>' + self.$target.attr("data-collection_name") + '</h2></div></div>');
            }
            if(!self.editableMode){
                $.get("/shop/get_product_snippet_content",{
                    'snippet_type': self.$target.attr('data-snippet_type') || '',
                    'collection_id': self.$target.attr('data-collection_id') || 0,
                    'snippet_layout': self.$target.attr('data-snippet_layout') || ''
                }).then(function( data ) {
                    if(data){
                        self.$target.empty().append(data);
                        if(self.$target.attr('data-snippet_layout') === 'slider' && self.$target.find('> .prod_slider').length === 1){
                            initialize_owl_1(self.$target.find("> .prod_slider .tqt-pro-slide"));
                        }
                        else if(self.$target.attr('data-snippet_layout') === 'fw_slider' && self.$target.find('> .fw_prod_slider').length === 1){
                            initialize_owl(self.$target.find("> .fw_prod_slider .tqt-pro-slide"));
                        }
                        // $(".sale_of_content").removeClass('hidden');
                        else if(self.$target.attr('data-snippet_layout') === 'slider_img_left' && self.$target.find('> .prod_slider_img_left').length === 1){
                            self.$target.find("> .prod_slider_img_left .p-slider-content_block .owl-carousel").owlCarousel({
                                items: 4,
                                margin: 0,
                                navigation: true,
                                pagination: true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    481: {
                                        items: 2,
                                    },
                                    768: {
                                        items: 2,
                                    },
                                    1024: {
                                        items: 4,
                                    }
                                }
                            });
                        }
                        else if(self.$target.attr('data-snippet_layout') === 'grid' && self.$target.find('> .prod_grid').length === 1){
                            
                        }
                        else if(self.$target.attr('data-snippet_layout') === 'fw_grid' && self.$target.find('> .fw_prod_grid').length === 1){
                            
                        }
                        else if(self.$target.attr('data-snippet_layout') === 'horiz_tab' && self.$target.find('> .h_tab_prod_snip').length === 1){
                            // self.$target.find("> .h_tab_prod_snip 'a[data-toggle='tab']")
                            self.$target.find('> .h_tab_prod_snip a[data-toggle="tab"]').on('shown.bs.tab', function () {
                                initialize_owl_multi(self.$target.find("> .h_tab_prod_snip .tab-content .active .multi_slider"));
                            }).on('hide.bs.tab', function () {
                                destory_owl(self.$target.find("> .h_tab_prod_snip .tab-content .active .multi_slider"));
                            });
                            initialize_owl_multi(self.$target.find("> .h_tab_prod_snip .tab-content .active .multi_slider"));
                        }
                        else if(self.$target.attr('data-snippet_layout') === 'vertic_tab' && self.$target.find('> .v_tab_prod_snip').length === 1){
                            
                        }
                        else{}
                    }
                });
            }
        }
    });

    sAnimation.registry.latest_blog_snippet_s = sAnimation.Class.extend({
        selector : ".as-blog-option-02",
        start: function (editMode) {
            var self = this;
            if (self.editableMode){
                self.$target.empty().append('<div class="container">Latest Blog Snippet 2</div>');
            }
            if(!self.editableMode){
                $.get("/shop/get_latest_blog_snip_content",{}).then(function( data ) {
                    if(data){
                        self.$target.empty().append(data);
                        $(".as-blog-option-02").removeClass('hidden');
                    }
                });
            }
        }
    });
});
