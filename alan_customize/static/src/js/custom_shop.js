odoo.define('alan_customize.customs_shop_js', function(require){
    'use strict';
    
    var ajax = require('web.ajax');


    
    $(document).on('click', '#load_more_products', function(){
        var $btnEle = $(this);
        var $products_grid = $("div#products_grid");
        $btnEle.siblings(".wait_loader_gif").removeClass("hidden");
        var temp_attr_list = [];
        if($("form.js_attributes").length > 0){
            $("form.js_attributes ul input:checked, form.js_attributes ul select option:selected").each(function(){
                temp_attr_list.push($(this).val());
            });
        }
        var param_dict = {
            loaded_products: $btnEle.siblings("input[name='loaded_products_count']").val(),
            ppg: parseInt($products_grid.find("div.shop-filter-item_qty select.custom-select").val() || 10),
            category: $btnEle.siblings("input[name='curr_category']").val(),
            search: $(".as-search form input[name='search']").val(),
            'attrib': temp_attr_list
        }
        if($btnEle.siblings("input[name='product_collection']").val() !== "-1"){
            param_dict.product_collection = $btnEle.siblings("input[name='product_collection']").val();
        }
        if($("#products_grid_before #price_filter_input").length > 0){
            param_dict.min_val = $('#min_val').val();
            param_dict.max_val = $('#max_val').val();
        }
        var order_val = $products_grid.find(".products_pager .dropdown_sorty_by > a.dropdown-toggle").attr("data-sort_key_value");
        if(order_val !== '')
            param_dict.order = order_val;
        $.get("/shop/load_next_products", param_dict).then(function(data){
            if(data.trim()){
                $btnEle.siblings(".wait_loader_gif").addClass("hidden");
                $("div#products_grid div.as-product-list > .row:first").append(data);
                $btnEle.siblings("input[name='loaded_products_count']").val($("div#products_grid div.as-product-list > .row:first > div > form[action='/shop/cart/update']").length);
                $.getScript("/alan_customize/static/src/js/wishlist.js");
            }
            else{
                $btnEle.text("No More Products").addClass("disabled");
            }
        });
    });

    $(document).on('change', 'div#products_grid div.shop-filter-item_qty select.custom-select', function(){
        var $selEle = $(this);
        var $products_grid = $("div#products_grid");
        var temp_attr_list = [];
        if($("form.js_attributes").length > 0){
            $("form.js_attributes > input[name='ppg']").val($selEle.val())
            $("form.js_attributes ul input:checked, form.js_attributes ul select option:selected").each(function(){
                temp_attr_list.push($(this).val());
            });
        }
        if($selEle.attr("data-shop_layout_type") === "0"){
            var $pagination_qty_change_form = $selEle.siblings("form.pagination_qty_change");
            $pagination_qty_change_form.find("input[name='ppg']").val($selEle.val());
            for(var i = 0; i < temp_attr_list.length; i++)
                $pagination_qty_change_form.append("<input type='text' class='hidden' name='attrib' value='" + temp_attr_list[i] + "'>");
            if($(".as-search form input[name='search']").val())
                $pagination_qty_change_form.append("<input type='text' class='hidden' name='search' value='" + $(".as-search form input[name='search']").val() + "'>");
            if($pagination_qty_change_form.find("input[name='category']").val()){
                $pagination_qty_change_form.attr("action", "/shop/category/" + $pagination_qty_change_form.find("input[name='category']").val());
            }
            $pagination_qty_change_form.find("input[name='category']").remove();
            $pagination_qty_change_form.trigger('submit');
        }
        else if($selEle.attr("data-shop_layout_type") === "1"){
            var $btnEle = $("#load_more_products");
            $btnEle.siblings(".wait_loader_gif").removeClass("hidden");
            $btnEle.text("LOAD MORE").removeClass("disabled");
            var param_dict = {
                loaded_products: 0,
                ppg: parseInt($selEle.val()),
                // category: $btnEle.siblings("input[name='curr_category']").val(),
                search: $(".as-search form input[name='search']").val(),
                'attrib': temp_attr_list
            };
            if($btnEle.siblings("input[name='curr_category']").length > 0){
                param_dict.category = $btnEle.siblings("input[name='curr_category']").val();
            }
            else{
                param_dict.category = $("div#products_grid_before div#active_categ.active_categ").html().trim();
            }
            if($btnEle.siblings("input[name='product_collection']").val() !== "-1"){
                param_dict.product_collection = $btnEle.siblings("input[name='product_collection']").val();
            }
            if($("#products_grid_before #price_filter_input").length > 0){
                param_dict.min_val = $('#min_val').val();
                param_dict.max_val = $('#max_val').val();
            }
            var order_val = $products_grid.find(".products_pager .dropdown_sorty_by > a.dropdown-toggle").attr("data-sort_key_value");
            if(order_val !== '')
                param_dict.order = order_val;
            console.log(param_dict);
            $.get("/shop/load_next_products", param_dict).then(function(data){
                if(data.trim()){
                    $btnEle.siblings(".wait_loader_gif").addClass("hidden");
                    $("div#products_grid div.as-product-list > .row:first").empty().append(data);
                    $btnEle.siblings("input[name='loaded_products_count']").val($("div#products_grid div.as-product-list > .row:first > div > form[action='/shop/cart/update']").length);
                    $.getScript("/website_sale_wishlist/static/src/js/website_sale_wishlist.js");
                    $.getScript("/website_sale_comparison/static/src/js/website_sale_comparison.js");
                    $.getScript("/alan_customize/static/src/js/frontend_product_quick_view_js.js");
                }
                else{
                    $btnEle.text("No More Products").addClass("disabled");
                }
            });
        }
        else{
            console.log("The html has been compromised!");
        }
    });
    
    var change_in_price_filter = false;
    $("#price_filter_input").slider();
    $(document).on("change", "#price_filter_input", function(){
        if($(this).val()){
            var prices = $(this).val().split(",");
            $('#min_val').val(prices[0]);
            $('#max_val').val(prices[1]);
            $('span.text_min_val').text(prices[0]);
            $('span.text_max_val').text(prices[1]);
            change_in_price_filter = true;
        }
    });
    $(document).on("click", "#products_grid_before .apply_price_filter", function(){
        $("#products_grid_before form.js_attributes").submit();
    });

    $(document).ready(function(){
        if($(".oe_website_sale").length === 0){
            $("div#wrap").addClass("oe_website_sale");
        }
        $(".o_twitter, .o_facebook, .o_linkedin, .o_google").on('click', function(event){
            var url = '';
            var product_title_complete = $('#product_details h1').html().trim() || '';
            if ($(this).hasClass('o_twitter')){
                url = 'https://twitter.com/intent/tweet?tw_p=tweetbutton&text=Amazing product : '+product_title_complete+"! Check it live: "+window.location.href;
            } else if ($(this).hasClass('o_facebook')){
                url = 'https://www.facebook.com/sharer/sharer.php?u='+window.location.href;
            } else if ($(this).hasClass('o_linkedin')){
                url = 'https://www.linkedin.com/shareArticle?mini=true&url='+window.location.href+'&title='+product_title_complete;
            } else if ($(this).hasClass('o_google')){
                url = 'https://plus.google.com/share?url='+window.location.href;
            } else{}
            window.open(url, "", "menubar=no, width=500, height=400");
        });

        /*$(".navbar-default #my_cart").on("click", function(e){
            $.get("/shop/cart", {type: 'cart_lines_popup'}).then(function(data){
                if(data.trim()){
                    var $mini_cart_popup = $(".navbar-default #my_cart > .cart_lines_popup");
                    $mini_cart_popup.empty().append(data.trim()).addClass("show_mini_cart");
                }
            });
            e.stopPropagation();
        });*/
        // $(".navbar-default #my_cart .cart_lines_popup").on("click", function(e){
        //     $(this).removeClass("show_mini_cart");
        //     e.stopPropagation();
        // });

        $("#wrapwrap header #my_cart .my_cart_btn").on("click", function(e){
            var $target = $(this);
            $.get("/shop/cart", {type: 'cart_lines_popup'}).then(function(data){
                if(data.trim()){
                    var $mini_cart_popup = $target.parents("header").find(".cart_lines_popup");
                    $mini_cart_popup.empty().append(data.trim()).addClass("show_mini_cart");
                }
            });
            e.stopPropagation();
        });
        $(document).on("click", "header .cart_lines_popup .m_c_close", function(){
            $(this).parents(".cart_lines_popup").removeClass("show_mini_cart");
        });


        $("#products_grid_before .js_attributes .clear_attr_filter").on("click", function(e){
            e.stopPropagation();
            var $attr_box = $(this).parents("li");
            var selected_vals = $(this).data("attr_value_ids");
            var val_selector_str = "";
            // for(var i = 0; i < selected_vals.length; i++){
            //     val_selector_str += "input[" + $(this).data("attr_id") + "-" + selected_vals[0] + "]";
            //     if(i != selected_vals.length - 1)
            //         val_selector_str += ",";
            // }
            // $attr_box.find(val_selector_str).prop
            $attr_box.find("input[name='attrib'][value^='" + $(this).data("attr_id") + "-']").each(function(){
                $(this).prop("checked", false);
            });
            $attr_box.find("select[name='attrib']").val("");
            $(this).parents("form.js_attributes").submit();
        });
        $("#products_grid_before .js_attributes .collapsible_attr_name").on("click", function(){
            $(this).toggleClass("section_open");
        });
    });
});
