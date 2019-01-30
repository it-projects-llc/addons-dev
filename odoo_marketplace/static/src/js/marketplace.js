/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('odoo_marketplace.WebClient', function (require) {
    "use strict";
    var ajax = require('web.ajax');

    $(document).ready(function() {
	    var temp=1

        // Apply customize css on website comments
        $('section#seller_review_discussion section#discussion section.mb32.hidden-print form.o_website_chatter_form img.img.pull-left.img-circle').css({ 'width': '30px',
    'margin-right': '10px'});
        $('section#seller_review_discussion section#discussion section.mb32.hidden-print form.o_website_chatter_form div.pull-left.mb32').css({ 'width': '95%'});
        $('section#seller_review_discussion section#discussion section.mb32.hidden-print form.o_website_chatter_form textarea').attr("rows", "2");
        $('section#seller_review_discussion section#discussion ul.media-list.o_website_comments div.media-body img.media-object.pull-left.img-circle').css({ 'width': '30px',
    'margin-right': '10px'});
        $('section#seller_review_discussion section#discussion section.mb32.hidden-print form.o_website_chatter_form div.pull-left.mb32 button').addClass("btn-xs");

        // Show marketplace term and conditions on website signup page
        function check_is_seller($this){
            var $div = $this.closest('div');
            var $mp_seller_details = $div.find('#mp_seller_details');
            var $profile_url = $mp_seller_details.find('#profile_url');
            var $country_id = $mp_seller_details.find('#country_id');
            var $mp_terms_conditions = $mp_seller_details.find('#mp_terms_conditions');
            if ($this.prop('checked'))
            {
                $mp_seller_details.show();
                $profile_url.attr('required','required');
                $country_id.attr('required','required');
                $mp_terms_conditions.attr('required','required');
            }
            else
            {
                $mp_seller_details.hide();
                $profile_url.removeAttr('required');
                $country_id.removeAttr('required');
                $mp_terms_conditions.removeAttr('required');
            }
        }
        $('#is_seller').each(function(){
            check_is_seller($(this));
        });
        $('#mp_terms_conditions').attr('checked',false);

        $(document).ready(function(){
            $('[data-toggle="popover"]').popover({container: '.url_info'});
        });

        $(document).on("click","#mp_t_and_c", function()
		{
            var term_condition = $('#mp_t_and_c_data').data("terms");
            var mp_t_and_c = 'No Terms and Conditions.';
            if($(term_condition).text().trim().length > 0){
                mp_t_and_c = term_condition;
            }
            ajax.jsonRpc("/mp/terms/and/conditions", 'call',{
                'mp_t_and_c': mp_t_and_c,
            })
            .then(function (modal) {
                var $modal = $(modal);
                $modal.appendTo('body')
                    .modal('show')
                    .on('hidden.bs.modal', function () {
                        $(this).remove();
                    });
            });

        });
        $(document).on("change","#is_seller", function()
		{
            check_is_seller($(this));
        });
        function validate_profile_url($url_value){

            var profile_url = String($url_value.val());
            var $profile_div = $url_value.closest('.has-feedback');
            var $form = $url_value.closest('.oe_signup_form');
            var $button_div = $form.find(".oe_login_buttons :button");
            $button_div.attr({'disabled':'disabled'})
            var $profile_span = $profile_div.find('.form-control-feedback');
            if($('#profile_url').hasClass('invalide_url')){
                $('#profile_url').removeClass('invalide_url');
            }
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
                $profile_div.addClass('has-error');
                $('#profile_url_error').html('Only alphanumeric([0-9],[a-z]) and some special characters(-,_) are allowed, Spaces are not allowed.');
                $('#profile_url').addClass('invalide_url');
                $('#mp_terms_conditions').attr('checked',false);
                $('#profile_url_error').show();
            }
            else{
                if(profile_url != '' && profile_url.match(/^[-_][a-zA-Z0-9-_]*$/) || profile_url.match(/^[a-zA-Z0-9-_]*[-_]$/)){
                    $profile_div.addClass('has-error');
                    $('#profile_url_error').html('Special characters are not allowed in begining or at the last of the string.');
                    $('#profile_url').addClass('invalide_url');
                    $('#mp_terms_conditions').attr('checked',false);
                    $('#profile_url_error').show();
                }
                else{
                    $profile_span.addClass('fa-spinner fa-pulse');
                    ajax.jsonRpc("/profile/url/handler/vaidation", 'call', {'url_handler': profile_url})
    				.then(function (vals)
    				{
                        $button_div.attr({'disabled': false})
                        if(vals && profile_url != ''){
                            if($profile_div.hasClass('has-error')){
                                $profile_div.removeClass('has-error');
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
                            $profile_div.addClass('has-success');
                            $profile_span.addClass('fa-check');
                            $('#profile_url_error').hide();
                        }
                        else{
                            if($profile_div.hasClass('has-success')){
                                $profile_div.removeClass('has-success');
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
                            $profile_div.addClass('has-error');
                            $profile_span.addClass('fa-times');
                            if(profile_url != ''){
                                $('#profile_url_error').html('Sorry, this profile url is not available.');
                            }
                            else{
                                $('#profile_url_error').html('Please Enter Your Profile URL.');
                            }
                            $('#profile_url').addClass('invalide_url');
                            $('#profile_url_error').show();
                            $('#mp_terms_conditions').attr('checked',false);
                        }
                    });
                }
            }
        }
        $(document).on("change","#mp_terms_conditions", function()
		{
            validate_profile_url($('#profile_url'));
        });
        $(document).on("input","#profile_url", function()
		{
            validate_profile_url($(this));
        });


        // Load recently added product of seller on the shop page
	    $('#recently_product_tab').click(function(e){
	    	var ajax = require('web.ajax');
	    	var return_qty;
			var shop_id = parseInt($(this).find('#shop_id').first().val(),10);
	    	if (temp === 1){
				$('.mp-box-review_loader').show();
				ajax.jsonRpc("/seller/shop/recently-product/", 'call', {'shop_id': shop_id})
				.then(function (vals)
				{
		            var $modal = $(vals);
		            temp = temp+1;
					$modal.appendTo('#tab22');
					$('.mp-box-review_loader').hide();
		        });
	    	}
            e.preventDefault(e);
        });

		// Load recently added product of seller on the profile page
	    $('#profile_recently_product_tab').click(function(e){
	    	var ajax = require('web.ajax');
	    	var seller_id = parseInt($(this).find('#seller_id').first().val(),10);
			if (temp === 1){
				$('.mp-box-review_loader').show();
                ajax.jsonRpc("/seller/profile/recently-product/", 'call', {'seller_id': seller_id})
    			.then(function (vals)
    			{
    	            var $modal = $(vals);
                    temp = temp+1;
					$modal.appendTo('#seller_recent_prod');
					$('.mp-box-review_loader').hide();
    	        });
                }
            e.preventDefault(e);
		});

        // Sale order line information for marketplace product
       	$('.sol-info').on('click', function()
        {
        	var order_line =  parseInt($(this).siblings('#mp_order_line').first().val(),10);
        	var ajax = require('web.ajax');
        	var self = this;
			ajax.jsonRpc("/track/sol", 'call', {'sol_id': order_line})
			.then(function (vals)
			{
				if (vals)
					var popover_containt = vals;
				else
					var popover_containt = "Information not found!!!";
				$(self).popover({
		            placement :"left",
		            title:"<center>More Information</center>",
		            trigger : 'focus',
		            html : true,
		            content :  String(popover_containt)
		        });
	            $(self).popover('show');
	            $(self).on('mouseleave', function()
	            {
	               $(self).popover('destroy');
	            });
	        });

        });
        // var box_flag = false;
        // var comments_flag = false;
       	// $('.seller-review-write-comments').on('click', function()
        // {
        // 	if (box_flag)
        // 	{
        // 		$("#seller-review-comment-box").hide();
        // 		box_flag = false;
        // 	}
        // 	else
        // 	{
        // 		$("#seller-review-comment-box").show();
        // 		box_flag = true;
        // 	}
        // });

        // $('.seller-review-comments').on('click', function()
        // {
        // 	if (comments_flag)
        // 	{
        // 		$("#seller-review-all-comment").hide();
        // 		comments_flag = false;
        // 	}
        // 	else
        // 	{
        // 		$("#seller-review-all-comment").show();
        // 		comments_flag = true;
        // 	}
        // });
	});
});
