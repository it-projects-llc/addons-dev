odoo.define('kingfisher_pro.kingfisher_pro_frontend_js', function(require) {
    'use strict';

    var animation = require('web_editor.snippets.animation');
    var ajax = require('web.ajax');

    animation.registry.kingfisher_pro_product_category_slider = animation.Class.extend({

        selector: ".oe_pro_cat_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('.oe_pro_cat_slider .owl-carousel').empty();
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-prod-cat-slider-type');
                $.get("/kingfisher_pro/pro_get_dynamic_slider", {
                    'slider-type': self.$target.attr('data-prod-cat-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_pro_cat_slider").removeClass('hidden');

                        ajax.jsonRpc('/kingfisher_pro/pro_image_effect_config', 'call', {
                            'slider_type': slider_type
                        }).done(function(res) {
                            _.each(self.$target.find('.cs-product'), function(k, v) {
                                if ($(k).find('.o_rating_star_card')) {
                                    var input_val = $(k).find('.o_rating_star_card').find("input").data('default');
                                    if (input_val > 0) {
                                        var rating = require('rating.rating');
                                        var rating_star = new rating.RatingStarWidget(this, {
                                            'rating_default_value': input_val,
                                            'rating_disabled': true,
                                        });
                                        if (rating_star) {
                                            $(k).find('.rating').empty();
                                            rating_star.appendTo($(k).find('.rating'));
                                        }
                                    }
                                }
                            });

                            $('div#' + res.s_id).owlCarousel({
                                margin: 10,
                                responsiveClass: true,
                                items: res.counts,
                                loop: true,
                                autoPlay: res.auto_rotate && res.auto_play_time,
                                stopOnHover: true,
                                navigation: true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 2,
                                    },
                                    768: {
                                        items: 3,
                                    },
                                    1000: {
                                        items: res.counts,
                                    },
                                    1500: {
                                        items: res.counts,
                                    },
                                },
                            });
                        });
                    }
                });
            }
        }
    });

    animation.registry.kingfisher_pro_brand_custom_slider = animation.Class.extend({

        selector: ".king_pro_brand_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('.king_pro_brand_slider .owl-carousel').empty();
            }
            if (!editable_mode) {
                $.get("/king_pro/get_brand_slider", {
                    'product_count': self.$target.attr('data-brand-count') || 0,
                    'product_label': self.$target.attr('data-product-label') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".king_pro_brand_slider").removeClass('hidden');

                        $('div#kingfisher_pro_brand_slider').owlCarousel({
                            margin: 10,
                            loop: true,
                            autoPlay: 9000,
                            stopOnHover: true,
                            navigation: true,
                            responsiveClass: true,
                            responsive: {
                                0: {
                                    items: 1,
                                },
                                420: {
                                    items: 2,
                                },
                                768: {
                                    items: 4,
                                },
                                1000: {
                                    items: 6,
                                },
                                1500: {
                                    items: 6,
                                },
                            },
                        });
                    }
                });
            }
        }
    });

    animation.registry.kingfisher_pro_blog_custom_snippet = animation.Class.extend({

        selector: ".king_pro_blog_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('.king_pro_blog_slider .owl-carousel').empty();
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-blog-slider-type');
                $.get("/kingfisher_pro/blog_get_dynamic_slider", {
                    'slider-type': self.$target.attr('data-blog-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".king_pro_blog_slider").removeClass('hidden');

                        ajax.jsonRpc('/kingfisher_pro/blog_image_effect_config', 'call', {
                            'slider_type': slider_type
                        }).done(function(res) {

                            $('div#' + res.s_id).owlCarousel({
                                margin: 10,
                                responsiveClass: true,
                                items: res.counts,
                                loop: true,
                                autoPlay: res.auto_rotate && res.auto_play_time,
                                stopOnHover: true,
                                navigation: true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 2,
                                    },
                                    768: {
                                        items: res.counts,
                                    },
                                    1000: {
                                        items: res.counts,
                                    },
                                    1500: {
                                        items: res.counts,
                                    }
                                },
                            });
                        });

                    }
                });
            }
        }
    });

    animation.registry.kingfisher_pro_multi_cat_custom_snippet = animation.Class.extend({

        selector: ".oe_multi_category_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('.oe_multi_category_slider .owl-carousel').empty();
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-multi-cat-slider-type');
                $.get("/kingfisher_pro/product_multi_get_dynamic_slider", {
                    'slider-type': self.$target.attr('data-multi-cat-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_multi_category_slider").removeClass('hidden');

                        ajax.jsonRpc('/kingfisher_pro/product_multi_image_effect_config', 'call', {
                            'slider_type': slider_type
                        }).done(function(res) {
                            _.each(self.$target.find('.cs-product'), function(k, v) {
                                if ($(k).find('.o_rating_star_card')) {
                                    var input_val = $(k).find('.o_rating_star_card').find("input").data('default');
                                    if (input_val > 0) {
                                        var rating = require('rating.rating');
                                        var rating_star = new rating.RatingStarWidget(this, {
                                            'rating_default_value': input_val,
                                            'rating_disabled': true,
                                        });
                                        if (rating_star) {
                                            $(k).find('.rating').empty();
                                            rating_star.appendTo($(k).find('.rating'));
                                        }
                                    }
                                }
                            });
                            $('.multi_hide .owl-carousel').owlCarousel({
                                margin: 10,
                                responsiveClass: true,
                                items: 4,
                                loop: true,
                                autoPlay: res.sliding_speed,
                                stopOnHover: true,
                                navigation: true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 2,
                                    },
                                    767: {
                                        items: 3,
                                    },
                                    1000: {
                                        items: 4,
                                    },
                                    1500: {
                                        items: 4,
                                    },
                                },
                            });
                        });

                    }
                });
            }
        }
    });

});