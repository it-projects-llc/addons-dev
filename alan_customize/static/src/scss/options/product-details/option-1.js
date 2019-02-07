$(document).ready(function() {

      // 1- Get window width 
      var windowWidth = $(window).width();

      // 2- For all devices under or at 768px, use horizontal orientation
      if(windowWidth <= 767) {
        $('.thumbnails-slides').slick({
            dots: false,
            infinite: true,
            speed: 300,
            slidesToShow: 3,
            vertical: false,
            centerMode: true,
            centerPadding: '40px',
            nextArrow: '<button type="button" class="next ti-angle-down"></button>',
            prevArrow: '<button type="button" class="prev ti-angle-up"></button>'
        });
      } 
      // 3- For all devices over 768px, use vertical orientation
      else {
        $('.thumbnails-slides').slick({
            dots: false,
            loop: true,
            arrows:true,
            infinite: true,
            speed: 300,
            slidesToShow: 5,
            centerMode: false,
            verticalSwiping: true,
            vertical: true,
            nextArrow: '<button type="button" class="next ti-angle-down"></button>',
            prevArrow: '<button type="button" class="prev ti-angle-up"></button>'
        });
      }
});

