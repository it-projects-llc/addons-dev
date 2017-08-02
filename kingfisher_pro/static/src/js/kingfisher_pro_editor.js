odoo.define('kingfisher_pro.kingfisher_pro_editor_js', function(require) {
    'use strict';

    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    ajax.loadXML('/kingfisher_pro/static/src/xml/kingfisher_pro.xml', qweb);

    options.registry.kingfisher_pro_product_category_slider = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".oe_pro_cat_slider .owl-carousel").empty();
            if (!editMode) {
                self.$el.find(".oe_pro_cat_slider").on("click", _.bind(self.pro_cat_slider, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.pro_cat_slider()) {
                this.pro_cat_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.oe_pro_cat_slider .owl-carousel').empty();
        },

        pro_cat_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(qweb.render("kingfisher_pro.king_pro_dynamic_product_category_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#slider_type"),
                    $cancel = self.$modal.find("#cancel"),
                    $pro_cat_sub_data = self.$modal.find("#pro_cat_sub_data");

                ajax.jsonRpc('/kingfisher_pro/pro_get_options', 'call', {}).done(function(res) {
                    $('#slider_type option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_type'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_cat_sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-prod-cat-slider-type', $slider_type.val());
                    self.$target.attr('data-prod-cat-slider-id', 'prod-cat-myowl' + $slider_type.val());
                    if ($('select#slider_type').find(":selected").text()) {
                        type = _t($('select#slider_type').find(":selected").text());
                    } else {
                        type = _t("Product/Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="row oe_our_slider">\
                                                        <div class="col-md-12">\
                                                            <div class="title-block">\
                                                                <h4 class="section-title style1">\
                                                                    <span>' + type + '</span>\
                                                                </h4>\
                                                            </div>\
                                                        </div>\
                                                    </div>\
                                                </div>');
                });
            } else {
                return;
            }
        },
    });

    options.registry.kingfisher_pro_brand_custom_slider = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".king_pro_brand_slider .owl-carousel").empty();
            if (!editMode) {
                self.$el.find(".king_pro_brand_slider").on("click", _.bind(self.king_brand_slider, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.king_brand_slider()) {
                this.king_brand_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.king_pro_brand_slider .owl-carousel').empty();
        },

        king_brand_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(qweb.render("kingfisher_pro.king_pro_brands_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $product_count = self.$modal.find("#brand-count"),
                    $product_label = self.$modal.find("#product-label"),
                    $cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#brand_sub_data");

                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr("data-brand-count", $product_count.val());
                    self.$target.attr('data-product-label', $product_label.val());

                    if ($product_label.val()) {
                        type = $product_label.val();
                    } else {
                        type = _t("Our Brands");
                    }

                    self.$target.empty().append('<div class="container">\
                                                    <div class="row our-brands">\
                                                        <div class="col-md-12">\
                                                            <div class="title-block">\
                                                                <h4 class="section-title style1">\
                                                                    <span>' + type + '</span>\
                                                                </h4>\
                                                            </div>\
                                                        </div>\
                                                    </div>\
                                                </div>');
                });
            } else {
                return;
            }
        },
    });

    options.registry.kingfisher_pro_blog_custom_snippet = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.king_pro_blog_slider .owl-carousel').empty();
            if (!editMode) {
                self.$el.find(".king_pro_blog_slider").on("click", _.bind(self.king_blog_slider, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.king_blog_slider()) {
                this.king_blog_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.king_pro_blog_slider .owl-carousel').empty();
        },

        king_blog_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(qweb.render("kingfisher_pro.king_pro_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#blog_slider_type"),
                    $cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/kingfisher_pro/blog_get_options', 'call', {}).done(function(res) {
                    $('#blog_slider_type option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_type'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_type.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_type.val());
                    if ($('select#blog_slider_type').find(":selected").text()) {
                        type = _t($('select#blog_slider_type').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="row">\
                                                        <div class="col-md-12">\
                                                            <div class="title-block">\
                                                                <h4 class="section-title style1">\
                                                                    <span>' + type + '</span>\
                                                                </h4>\
                                                            </div>\
                                                        </div>\
                                                    </div>\
                                                </div>');
                });
            } else {
                return;
            }
        },
    });

    options.registry.kingfisher_pro_multi_cat_custom_snippet = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.oe_multi_category_slider .owl-carousel').empty();
            if (!editMode) {
                self.$el.find(".oe_multi_category_slider").on("click", _.bind(self.multi_category_slider, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.multi_category_slider()) {
                this.multi_category_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.oe_multi_category_slider .owl-carousel').empty();
        },

        multi_category_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(qweb.render("kingfisher_pro.multi_product_custom_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#slider_type"),
                    $cancel = self.$modal.find("#cancel"),
                    $snippnet_submit = self.$modal.find("#snippnet_submit");

                ajax.jsonRpc('/kingfisher_pro/product_multi_get_options', 'call', {}).done(function(res) {
                    $("select[id='slider_type'] option").remove();
                    _.each(res, function(y) {
                        $("select[id='slider_type']").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $snippnet_submit.on('click', function() {
                    // var type = '';
                    self.$target.attr('data-multi-cat-slider-type', $slider_type.val());
                    self.$target.attr('data-multi-cat-slider-id', 'multi-cat-myowl' + $slider_type.val());
                    if ($('select#slider_type').find(":selected").text()) {
                        var type = '';
                        type = _t($('select#slider_type').find(":selected").text());
                    } else {
                        var type = '';
                        type = _t("Multi Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="row our-categories">\
                                                        <div class="col-md-12">\
                                                            <div class="title-block">\
                                                                <h4 class="section-title style1">\
                                                                    <span>' + type + '</span>\
                                                                </h4>\
                                                            </div>\
                                                        </div>\
                                                    </div>\
                                                </div>');
                });
            } else {
                return;
            }
        },
    });

});