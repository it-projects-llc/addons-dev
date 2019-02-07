$(document).ready(function() {
    // zoom slider
    $('.main_image').hover(function(ev) {
        s = this.src;        
        $('.zoomContainer').remove();
        $('.product_detail_img').elevateZoom({
            constrainType: "height",
            constrainSize: 274,
            zoomType: "lens",
            containLensZoom: true,
            cursor: 'pointer'
        });
    });

    $(".slider-popup-product").hover(function() {
        $('.zoomContainer').remove();
        $('.product_detail_img').removeData('elevateZoom');
        $('.product_detail_img').elevateZoom({
            constrainType: "height",
            constrainSize: 274,
            zoomType: "lens",
            containLensZoom: true,
            cursor: 'pointer'
        });
    });
   

    $("img.sub-images").click(function(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        s = this.src;
        $('.main_image').attr('src', this.src);
        $('.main_image').parent().attr('href',this.src);
        $('div.zoomContainer').remove();
        $('.product_detail_img').removeData('elevateZoom');
        $('.product_detail_img').elevateZoom({
            constrainType: "height",
            constrainSize: 274,
            zoomType: "lens",
            containLensZoom: true,
            cursor: 'pointer'
        });
    });
});

