odoo.define('kingfisher_pro.kingfisher_pro_js', function(require) {
    'use strict';

    var ajax = require('web.ajax');

    // Dynamic cart update
    $(document).ready(function() {
        $('.oe_website_sale').each(function() {
            var oe_website_sale = this;
            var clickwatch = (function() {
                var timer = 0;
                return function(callback, ms) {
                    clearTimeout(timer);
                    timer = setTimeout(callback, ms);
                };
            })();

            $(oe_website_sale).on("change", ".oe_cart input.js_quantity[data-product-id]", function() {
                var $input = $(this);
                if ($input.data('update_change')) {
                    return;
                }
                var value = parseInt($input.val(), 10);
                var $dom = $(this).closest('tr');
                var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
                var line_id = parseInt($input.data('line-id'), 10);
                var product_id = parseInt($input.data('product-id'), 10);
                var product_ids = [product_id];
                clickwatch(function() {
                    $dom_optional.each(function() {
                        $(this).find('.js_quantity').text(value);
                        product_ids.push($(this).find('span[data-product-id]').data('product-id'));
                    });
                    $input.data('update_change', true);
                    ajax.jsonRpc("/shop/cart/update_json", 'call', {
                        'line_id': line_id,
                        'product_id': parseInt($input.data('product-id'), 10),
                        'set_qty': value
                    }).then(function(data) {
                        $input.data('update_change', false);
                        if (value !== parseInt($input.val(), 10)) {
                            $input.trigger('change');
                            return;
                        }
                        var $q1 = $(".king_pro_cart_quantity");
                        $q1.html(data.cart_quantity).hide().fadeIn(600);
                        $("#king_hover_total").replaceWith(data['kingfisher_pro.hover_total']);
                    });
                }, 500);

            });
        });

        // Multi image gallery
        ajax.jsonRpc('/kingfisher_pro/multi_image_effect_config', 'call', {})
            .done(function(res) {
                var dynamic_data = {}
                dynamic_data['gallery_images_preload_type'] = 'all'
                dynamic_data['slider_enable_text_panel'] = false
                dynamic_data['gallery_skin'] = "alexis"
                dynamic_data['gallery_height'] = 800

                if (res.theme_panel_position != false) {
                    dynamic_data['theme_panel_position'] = res.theme_panel_position
                }

                if (res.interval_play != false) {
                    dynamic_data['gallery_play_interval'] = res.interval_play
                }

                if (res.color_opt_thumbnail != false && res.color_opt_thumbnail != 'default') {
                    dynamic_data['thumb_image_overlay_effect'] = true
                    if (res.color_opt_thumbnail == 'b_n_w') {}
                    if (res.color_opt_thumbnail == 'blur') {
                        dynamic_data['thumb_image_overlay_type'] = "blur"
                    }
                    if (res.color_opt_thumbnail == 'sepia') {
                        dynamic_data['thumb_image_overlay_type'] = "sepia"
                    }
                }

                if (res.enable_disable_text == true) {
                    dynamic_data['slider_enable_text_panel'] = true
                }

                if (res.change_thumbnail_size == true) {
                    dynamic_data['thumb_height'] = res.thumb_height
                    dynamic_data['thumb_width'] = res.thumb_width
                }

                if (res.no_extra_options == false) {
                    dynamic_data['slider_enable_arrows'] = false
                    dynamic_data['slider_enable_progress_indicator'] = false
                    dynamic_data['slider_enable_play_button'] = false
                    dynamic_data['slider_enable_fullscreen_button'] = false
                    dynamic_data['slider_enable_zoom_panel'] = false
                    dynamic_data['slider_enable_text_panel'] = false
                    dynamic_data['strippanel_enable_handle'] = false
                    dynamic_data['gridpanel_enable_handle'] = false
                    dynamic_data['theme_panel_position'] = 'bottom'
                    dynamic_data['thumb_image_overlay_effect'] = false
                }

                $('#gallery').unitegallery(
                    dynamic_data
                );
            });

        // Price slider code start
        var minval = $("input#m1").attr('value'),
            maxval = $('input#m2').attr('value'),
            minrange = $('input#ra1').attr('value'),
            maxrange = $('input#ra2').attr('value'),
            website_currency = $('input#king_pro_website_currency').attr('value');

        if (!minval) {
            minval = 0;
        }
        if (!maxval) {
            maxval = maxrange;
        }
        if (!minrange) {
            minrange = 0;

        }
        if (!maxrange) {
            maxrange = 2000;
        }

        $("div#priceslider").ionRangeSlider({
            keyboard: true,
            min: parseInt(minrange),
            max: parseInt(maxrange),
            type: 'double',
            from: minval,
            to: maxval,
            step: 1,
            prefix: website_currency,
            grid: true,
            onFinish: function(data) {
                $("input[name='min1']").attr('value', parseInt(data.from));
                $("input[name='max1']").attr('value', parseInt(data.to));
                $("div#priceslider").closest("form").submit();
            },
        });
        // Price slider code ends

        //attribute remove code
        $("a#clear").on('click', function() {
            var url = window.location.href.split("?");
            var lival = $(this).closest("label").attr('id');
            ajax.jsonRpc("/kingfisher_pro/removeattribute", 'call', {
                'attr_remove': lival
            }).then(function(data) {
                if (data == true) {
                    window.location.href = url[0];
                }
            })
        });

    });
});
