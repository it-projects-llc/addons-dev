/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

$(document).ready(function() {
    $('.avg-rating-cir').percentcircle({
        animate : true,
        diameter : 130,
        guage: 6,
        coverBg: '#fff',
        bgColor: '#efefef',
        fillColor: '#E95546',
        percentSize: '15px',
        percentWeight: 'normal'
    });
        $('.recommendation-cir').percentcircle({
        animate : true,
        diameter : 130,
        guage: 6,
        coverBg: '#fff',
        bgColor: '#efefef',
        fillColor: '#5bc0de',
        percentSize: '15px',
        percentWeight: 'normal'
    });

    odoo.define('odoo_marketplace.seller_ratting', function (require)
    {
        "use strict";
        var ajax = require('web.ajax');
        var core = require('web.core');
        var _t = core._t;

        $("#rating-star").rating({
            starCaptions: {1: _t("Poor"), 2: _t("Ok"), 3: _t("Good"), 4: _t("Very Good"), 5: _t("Excellent")},
            starCaptionClasses: {1: "text-danger badge badge-danger", 2: "text-warning badge badge-warning", 3: "text-info badge badge-info", 4: "text-secondary badge badge-primary", 5: "text-success badge badge-success"},
        });

        $('#btn-create-review').on('click',function (e){
               var rate = $("#rating-star").val();
               var title = $("#title").val().trim();
               var review_summary = $("#summary").val().trim();
            if (rate<=0)
            {
                $("#submit-msg").empty();
                $("#submit-msg").html(_t(" Please add your rating !!!"));
                $("#submit-msg").addClass("alert-danger submit-error-msg fa fa-exclamation-triangle");
                $('#submit-msg').show();
            }
            else if(title == "")
            {
                $("#review-title-box").addClass("has-error");
                $("#submit-msg").html(_t(" Review title is required field."));
                $("#submit-msg").addClass("alert-danger submit-error-msg fa fa-exclamation-triangle");
                $('#submit-msg').show();
            }
            else if(review_summary == "")
            {
                $("#review-title-box").removeClass("has-error");
                $("#submit-msg").empty();
                $("#review-summary-box").addClass("has-error");
                $("#submit-msg").html(_t(" Review is required field."));
                $("#submit-msg").addClass("alert-danger submit-error-msg");
                $('#submit-msg').show();
            }
            else
            {
                $("#review-summary-box").removeClass("has-error alert-danger submit-error-msg");
                ajax.jsonRpc("/seller/review/check", 'call',
                {
                    'seller_id':seller_id,
                })
                .then(function (result)
                {
                    if (jQuery.type(result) == "boolean")
                    {
                        $('#btn-create-review').addClass('disabled');
                        var button_add_review_text = $('#btn-create-review').html()
                        $('#btn-create-review').html('<i class="fa fa-refresh fa-spin"></i> Posting...');
                        ajax.jsonRpc("/seller/review", 'call',
                        {
                            'seller_id':seller_id,
                            'stars':rate,
                            'title':title,
                            'review':review_summary,
                        })
                        .then(function (response)
                        {
                            $("#mp-review-form").trigger('reset');
                            if (response)
                            {
                                $("#submit-msg").html(response);
                                $("#submit-msg").removeClass("alert-danger alert-warning");
                                $("#submit-msg").addClass("alert-success submit-error-msg fa fa-check-circle");
                                setTimeout(function() {$('#submit-msg').hide()},3500);
                            }
                            else
                            {
                                $("#submit-msg").html(_t("  Your review has been submitted successfully. Thank you!"));
                                $("#submit-msg").removeClass("alert-danger alert-warning");
                                $("#submit-msg").addClass("alert-success submit-error-msg fa fa-check-circle");
                                setTimeout(function() {$('#submit-msg').hide()},3500);
                            }
                            $('#btn-create-review').removeClass('disabled');
                            $('#btn-create-review').html(button_add_review_text);
                        });
                    }
                    else
                    {
                        $("#submit-msg").html(result);
                        $("#submit-msg").removeClass("alert-danger");
                        $("#submit-msg").addClass("alert-warning submit-error-msg fa fa-exclamation-triangle");
                    }
                });
            }
        });

        $(document).on('keyup', '#review-title-box',function()
        {
            $("#review-title-box").removeClass("has-error");
            $("#submit-msg").removeClass(" alert-danger submit-error-msg fa fa-exclamation-triangle fa-check-circle alert-success");
            $("#submit-msg").empty();
        });
        $(document).on('keyup', '#review-summary-box',function()
        {
            $("#review-summary-box").removeClass("has-error");
            $("#submit-msg").removeClass("alert-danger submit-error-msg fa fa-exclamation-triangle alert-warning fa-check-circle alert-success");
            $("#submit-msg").empty();
        });

        var sort_by = "recent";
        var filter_by = -1;
        var offset = 0;
        var seller_id =  parseInt($('#seller_all_review').find('input[type="hidden"][name="seller_id"]').first().val(),10);

        $('#mp-load-morebtn').on('click',function (e)
        {
            var select_star = parseInt($('#select_star').val(),10);
            var total_seller_reviews = $('#total_seller_reviews').html();
            var limit =  parseInt($('#seller_all_review').find('input[type="hidden"][name="limit"]').first().val(),10);
            offset=offset+limit ;
            $("#mp-load-morebtn").hide();
            $("#mp-load-morebtn-loder").show();
            ajax.jsonRpc("/seller/load/review", 'call',
            {
                'seller_id':seller_id,
                'offset': offset,
                'limit': limit,
                'sort_by':sort_by,
                'filter_by':filter_by,
            })
            .then(function (result)
            {
                var $review =$(result);
                $review.appendTo('.mp-box-review');
                $("#mp-load-morebtn-loder").hide();
                $("#mp-load-morebtn").show();
            });


            ajax.jsonRpc("/seller/load/review/count", 'call',
            {
                'seller_id':seller_id,
                'offset': offset,
                'limit': limit,
                'sort_by':sort_by,
                'filter_by':filter_by,
            })
            .then(function (result)
            {
                if (result[0] > 0)
                    $('#viewed').text(offset+result[0]);
                if (total_seller_reviews == offset+result[0])
                    $('#mp-load-more-div').hide();
            });
        });

        // Code for updating reviews using nav-bar menus
        $('#select_star').on('click',function (e)
        {
            offset = 0;
            var select_star_offset = 0;
            filter_by = parseInt($('#select_star').val(),10);
            var limit =  parseInt($('#seller_all_review').find('input[type="hidden"][name="limit"]').first().val(),10);
            var total_seller_reviews = $('#total_seller_reviews').html();
            $('.mp-box-review_loader').show();
            ajax.jsonRpc("/seller/load/review", 'call',
            {
                'seller_id':seller_id,
                'offset': 0,
                'limit': limit,
                'sort_by':sort_by,
                'filter_by':filter_by,
            })
            .then(function (result)
            {
                var $review =$(result);
                $('.mp-box-review').html($review);
                $('.mp-box-review_loader').hide();
            });
            ajax.jsonRpc("/seller/load/review/count", 'call',
            {
                'seller_id':seller_id,
                'offset': offset,
                'limit': limit,
                'sort_by':sort_by,
                'filter_by':filter_by,
            })
            .then(function (result)
            {
                $('#viewed').text(select_star_offset+result[0]);
                if (result[1] == select_star_offset+result[0])
                    $('#mp-load-more-div').hide();
                else
                    $('#mp-load-more-div').show();
                $('#total_seller_reviews').text(result[1]);
            });
        });

        $('#most_helpful_tab').on('click',function (e)
        {
            offset = 0;
            sort_by = "most_helpful"
            var most_helpful_tab_offset = 0;
            var limit =  parseInt($('#seller_all_review').find('input[type="hidden"][name="limit"]').first().val(),10);
            var total_seller_reviews = $('#total_seller_reviews').html();
            $("#most_recent_tab").removeClass("active-sort-tab");
            $("#most_helpful_tab").addClass("active-sort-tab");
            $('.mp-box-review_loader').show();
            ajax.jsonRpc("/seller/load/review", 'call',
            {
                'seller_id':seller_id,
                'offset': most_helpful_tab_offset,
                'limit': limit,
                'sort_by':sort_by,
                'filter_by':filter_by,
            })
            .then(function (result)
            {
                var $review =$(result);
                $('.mp-box-review').html($review);
                $('.mp-box-review_loader').hide();
            });
            ajax.jsonRpc("/seller/load/review/count", 'call',
            {
                'seller_id':seller_id,
                'offset': most_helpful_tab_offset,
                'limit': limit,
                'sort_by':sort_by,
                'filter_by':filter_by,
            })
            .then(function (result)
            {
                if (result[0])
                    $('#viewed').text(most_helpful_tab_offset+result[0]);
                if (result[1] == most_helpful_tab_offset+result[0])
                    $('#mp-load-more-div').hide();
                else
                    $('#mp-load-more-div').show();
            });
        });

        $('#most_recent_tab').on('click',function (e)
        {
            offset = 0;
            sort_by = "recent"
            var most_recent_tab_offset = 0;
            var limit =  parseInt($('#seller_all_review').find('input[type="hidden"][name="limit"]').first().val(),10);
            var total_seller_reviews = $('#total_seller_reviews').html();
            $("#most_helpful_tab").removeClass("active-sort-tab");
            $("#most_recent_tab").addClass("active-sort-tab");
            $('.mp-box-review_loader').show();
            ajax.jsonRpc("/seller/load/review", 'call',
            {
                'seller_id':seller_id,
                'offset': 0,
                'limit': limit,
                'sort_by':sort_by,
                'filter_by':filter_by,
            })
            .then(function (result)
            {
                var $review =$(result);
                $('.mp-box-review').html($review);
                $('.mp-box-review_loader').hide();
            });
            ajax.jsonRpc("/seller/load/review/count", 'call',
            {
                'seller_id':seller_id,
                'offset': most_recent_tab_offset,
                'limit': limit,
                'sort_by':sort_by,
                'filter_by':filter_by,
            })
            .then(function (result)
            {
                if (result[0])
                    $('#viewed').text(most_recent_tab_offset+result[0]);
                if (result[1] == most_recent_tab_offset+result[0])
                    $('#mp-load-more-div').hide();
                else
                    $('#mp-load-more-div').show();
            });
        });


        $("body").on('click', ".mp-sprite", function(e){
            var $review_box_bottom = $(this).closest('.seller-review-bottom');
            if ($(this).hasClass('mp-TopLeft'))
            {
                $(this).removeClass('mp-TopLeft');
                $(this).addClass('mp-BottomLeft');

                var seller_review_id =  parseInt($(this).closest('.seller_review_div').find("#seller_review_id").val(),10);
                var review_help = 1;
                ajax.jsonRpc("/seller/review/help", 'call',
                {
                    'seller_review_id': seller_review_id,
                    'review_help': review_help
                })
                .then(function (result)
                {
                    if (result)
                    {
                        $review_box_bottom.find('.review_helpful').text(result[0]);
                        $review_box_bottom.find('.review_not_helpful').text(result[1]);
                    }
                });
                $('.seller_review_div .mp-BottomRight').addClass('mp-TopRight').removeClass('mp-BottomRight');
                return;
            }

            if ($(this).hasClass('mp-TopRight'))
            {
                $(this).removeClass('mp-TopRight');
                $(this).addClass('mp-BottomRight');
                var seller_review_id =  parseInt($(this).closest('.seller_review_div').find("#seller_review_id").val(),10);
                var review_help = -1;
                ajax.jsonRpc("/seller/review/help", 'call',
                {
                    'seller_review_id': seller_review_id,
                    'review_help': review_help
                })
                .then(function (result)
                {
                    if (result)
                    {
                        $review_box_bottom.find('.review_not_helpful').text(result[1]);
                        $review_box_bottom.find('.review_helpful').text(result[0]);
                    }
                });
                $('.seller_review_div .mp-BottomLeft').addClass('mp-TopLeft').removeClass('mp-BottomLeft');
                return;
            }
            if ($(this).hasClass('mp-BottomLeft'))
            {
                $(this).removeClass('mp-BottomLeft');
                $(this).addClass('mp-TopLeft');
                var seller_review_id =  parseInt($(this).closest('.seller_review_div').find("#seller_review_id").val(),10);
                var review_help = 2;
                ajax.jsonRpc("/seller/review/help", 'call',
                {
                    'seller_review_id': seller_review_id,
                    'review_help': review_help
                })

                .then(function (result)
                {
                    if (result)
                    {
                        $review_box_bottom.find('.review_helpful').text(result[0]);
                        $review_box_bottom.find('.review_not_helpful').text(result[1]);
                    }
                });
                return;
            }
            if ($(this).hasClass('mp-BottomRight'))
            {
                $(this).removeClass('mp-BottomRight');
                $(this).addClass('mp-TopRight');
                var seller_review_id =  parseInt($(this).closest('.seller_review_div').find("#seller_review_id").val(),10);
                var review_help = -2;
                ajax.jsonRpc("/seller/review/help", 'call',
                {
                    'seller_review_id': seller_review_id,
                    'review_help': review_help
                })
                .then(function (result)
                {
                    if (result)
                    {
                        $review_box_bottom.find('.review_not_helpful').text(result[1]);
                        $review_box_bottom.find('.review_helpful').text(result[0]);
                    }
                });
                return;
            }
        });

        $('#recommend-yes').on('click',function (e){
            ajax.jsonRpc('/seller/recommend', "call",
            {
                'seller_id':seller_id,
                "recommend_state":"yes"
            })
            .then(function (result)
            {

            });
            $(this).removeClass("btn-info");
            $(this).addClass("btn-success");
            $("#recommend-no").removeClass("btn-success");
            $("#recommend-no").addClass("btn-info");
            $("#seller-recommend").addClass("hide-comment");
            $("#recommend-vote").removeClass("hide-comment");
        });
        $('#recommend-no').on('click',function (e){
            ajax.jsonRpc('/seller/recommend', "call",
            {
                'seller_id':seller_id,
                "recommend_state":"no"
            })
            .then(function (result)
            {

            });
            $(this).removeClass("btn-info");
            $(this).addClass("btn-success");
            $("#recommend-yes").removeClass("btn-success");
            $("#recommend-yes").addClass("btn-info");
            $("#seller-recommend").addClass("hide-comment");
            $("#recommend-vote").removeClass("hide-comment");
        });
        $('#open-review-tab').click(function(e){
            e.preventDefault();
            $('#shop-nav-tabs a[href="#rating_review_tab"]').tab('show');
            $('html,body').animate({scrollTop: $("#seller-info-pannel").offset().top},'slow');
        })

        $(document).ready(function() {
            $("abbr.timeago").timeago();
        });
    });
});
