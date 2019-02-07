$(document).ready(function() {
      $('#as_accessory_product').slick({
            dots: false,
            infinite: false,
            speed: 300,
            slidesToShow: 1,
            centerMode: false,
            rows: 3,
            nextArrow: '<button type="button" class="next ti-angle-right"></button>',
            prevArrow: '<button type="button" class="prev ti-angle-left"></button>'
      });

      $('#as_alternative').slick({
            dots: false,
            infinite: false,
            speed: 300,
            slidesToShow: 1,
            rows: 3,
            centerMode: false,
            nextArrow: '<button type="button" class="next ti-angle-right"></button>',
            prevArrow: '<button type="button" class="prev ti-angle-left"></button>'
      });
});