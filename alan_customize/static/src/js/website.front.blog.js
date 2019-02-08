odoo.define('alan_customize.front_js_blog',function(require){
    'use strict';

    var utils = require('web.utils');
    var sAnimation = require('website.content.snippets.animation');

    sAnimation.registry.latest_blog = sAnimation.Class.extend({
        selector : ".web_blog_slider",
        start: function () {
            var self = this;
            if (self.editableMode){
                self.$target.empty().append('<div class="seaction-head"><h1>Blog Slider</h1></div>');
            }
            if (!this.editableMode) {
                var list_id=self.$target.attr('data-blog_list-id') || false;
                $.get("/blog/get_blog_content",{'blog_config_id':list_id}).then(function (data){
                    if(data){
                        self.$target.empty().append(data);
                        self.$target.removeClass("hidden");
                        $(".tqt-blog-slide").owlCarousel({
                            items: 4,
                            margin: 30,
                            nav: false,
                            dots: true,
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
                                    items: 3,
                                }
                            }
                        });
                    }
                });
            }
        },
    });
});
