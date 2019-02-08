odoo.define('alan_customize.product_image_gallery_js', function(require){
	'use strict';

	var ajax = require('web.ajax');
	var core = require('web.core');
	var qweb = core.qweb;

	// ajax.loadXML('/alan_customize/static/src/xml/image_slider_zoom.xml', qweb);

	$(document).ready(function(){
		// $("section#product_detail .product-img-box")
		var $img_slider = $("section#product_detail .product-img-box .thumbnails-slides");
		$("section#product_detail .product-img-box .img-gallery_popup").on('click', function(e){
			e.stopImmediatePropagation();
			console.log(e.isImmediatePropagationStopped());
			// var $modal = $(qweb.render('alan_customize.image_gallery_content'));
			// var close_button_str = '<button type="button" class="close" data-dismiss="modal">&times;</button>';
			var curr_slide_url = $(this).find("img.product_detail_img").prop('src');
			$.get('/get_product_img_gallery', {
				'product_id': $("#product_details .js_main_product input[name='product_id']").val()
			}).then(function(data){
				$("body #image_gallery_slider.modal").remove();
				if(data.trim()){
					$("body").append(data.trim());
					$("body > #image_gallery_slider.modal").modal();
					$("body > #image_gallery_slider.modal").on("shown.bs.modal", function(){
						$(this).find(".gallery_img.owl-carousel").owlCarousel({
							items: 1,
		                    margin: 0,
		                    navigation: true,
		                    pagination: true,
		                    // loop: true,
						});
						var goto_index = 0;
						$(this).find(".gallery_img.owl-carousel .item img.sub-images").each(function(index, obj){
							console.log(index, obj, $(this).prop('src'));
							if($(this).prop('src') === curr_slide_url)
								goto_index = index;
						});
						console.log("goto_index", goto_index);
						$(this).find(".gallery_img.owl-carousel").trigger('to.owl.carousel', goto_index);
					});
					// $modal.find(".image_gallery_content").empty().append(close_button_str + $("section#product_detail .product-img-box").html());
					// var $btn_close = $modal.find(".image_gallery_content > button.close");
					// $modal.modal();
					// $modal.on('click', $btn_close, function(){

					// });
				}

			});
		});
	});
});
