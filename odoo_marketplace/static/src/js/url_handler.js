/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('odoo_marketplace.test', function (require) {
'use strict';

    function validate_profile_url($url_value,data){
        var ajax = require('web.ajax');
        var profile_url = String($url_value.val());
        var $profile_span = $('.url_validation');
        var profile_or_shop_id = parseInt($('.profile_or_shop_id').text(),10);

        if($profile_span.hasClass('fa-pencil')){
            $profile_span.removeClass('fa-pencil');
        }
        if($profile_span.hasClass('fa-times')){
            $profile_span.removeClass('fa-times');
        }
        if($profile_span.hasClass('fa-check')){
            $profile_span.removeClass('fa-check');
        }
        if(profile_url != '' && !profile_url.match(/^[a-zA-Z0-9-_]+$/)){
            $url_value.addClass('url-error');
            $('#profile_url_error').html('Only alphanumeric([0-9],[a-z]) and some special characters(-,_) are allowed, Spaces are not allowed.');
            $('#profile_url_error').show();
        }
        else{

            if(profile_url != '' && profile_url.match(/^[-_][a-zA-Z0-9-_]*$/) || profile_url.match(/^[a-zA-Z0-9-_]*[-_]$/)){
                $url_value.addClass('url-error');
                $('#profile_url_error').html('Special characters are not allowed in begining or at the last of the string.');
                $('#profile_url_error').show();
            }
            else{
                $profile_span.addClass('fa-spinner fa-pulse');
                ajax.jsonRpc("/profile/url/handler/vaidation", 'call', {'url_handler': profile_url,'model':data,'profile_or_shop_id':profile_or_shop_id})
                .then(function (vals)
                {
                    if(vals && profile_url != ''){
                        if($url_value.hasClass('url-error')){
                            $url_value.removeClass('url-error');
                        }
                        if($profile_span.hasClass('fa-pencil')){
                            $profile_span.removeClass('fa-pencil');
                        }
                        if($profile_span.hasClass('fa-times')){
                            $profile_span.removeClass('fa-times');
                        }
                        if($profile_span.hasClass('fa-spinner fa-pulse')){
                            $profile_span.removeClass('fa-spinner fa-pulse');
                        }
                        $url_value.addClass('url-success');
                        $profile_span.addClass('fa-check');
                        $('#profile_url_error').hide();
                    }
                    else{
                        if($url_value.hasClass('url-success')){
                            $url_value.removeClass('url-success');
                        }
                        if($profile_span.hasClass('fa-pencil')){
                            $profile_span.removeClass('fa-pencil');
                        }
                        if($profile_span.hasClass('fa-check')){
                            $profile_span.removeClass('fa-check');
                        }
                        if($profile_span.hasClass('fa-spinner fa-pulse')){
                            $profile_span.removeClass('fa-spinner fa-pulse');
                        }
                        $url_value.addClass('url-error');
                        $profile_span.addClass('fa-times');
                        if(profile_url != ''){
                            $('#profile_url_error').html('Sorry, this profile url is not available.');
                        }
                        else{
                            $('#profile_url_error').html('Please Enter Your Profile URL.');
                        }
                        $('#profile_url_error').show();
                    }
                });
            }
        }
    }
    $(document).on("input",".profile_url", function()
    {
        validate_profile_url($(this),'res.partner');
    });
    $(document).on("input",".seller_shop_url", function()
    {
        validate_profile_url($(this),'seller.shop');
    });
});
