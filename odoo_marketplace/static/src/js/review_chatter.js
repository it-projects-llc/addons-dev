/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

$(document).ready(function () {
    odoo.define('odoo_marketplace.review_chatter', function (require){
        // Show/hide comment box and comments on seller reviews
        $(document).on('click', '.seller-review-write-comments', function () {
            console.log("Click on seller-review-write-comments");
            var $review_box = $(this).closest('.seller_review_div');
            $review_box.find("div.o_portal_chatter").show();
            if ($review_box.find("div.o_portal_chatter_composer").is(":visible")){
                $review_box.find("div.o_portal_chatter_composer").hide();
                if (! $review_box.find("div.o_portal_chatter_messages").is(":visible"))
                    $review_box.find("div.o_portal_chatter").hide();
            }
            else
                $review_box.find("div.o_portal_chatter_composer").show();
        });

        $(document).on('click', '.seller-review-comments', function () {
            console.log("Click on seller-review-comments");
            var $review_box = $(this).closest('.seller_review_div');
            $review_box.find("div.o_portal_chatter").show();
            if ($review_box.find("div.o_portal_chatter_messages").is(":visible")){
                $review_box.find("div.o_portal_chatter_messages").hide();
                if (!$review_box.find("div.o_portal_chatter_composer").is(":visible"))
                    $review_box.find("div.o_portal_chatter").hide();
            }
            else
                $review_box.find("div.o_portal_chatter_messages").show();
        });
    });
});