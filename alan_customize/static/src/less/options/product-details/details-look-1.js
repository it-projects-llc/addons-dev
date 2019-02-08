$(document).ready(function() {
      $("#as_accessory_product").owlCarousel({
        items: 4,
        margin: 30,
        navigation: true,
        pagination: false,
        responsive: {
            0: {
                items: 1,
            },
            481: {
                items: 2,
            },
            768: {
                items: 3,
            },
            1024: {
                items: 4,
            }
        }
      });

      $("#as_alternative").owlCarousel({
        items: 4,
        margin: 30,
        navigation: true,
        pagination: false,
        responsive: {
            0: {
                items: 1,
            },
            481: {
                items: 2,
            },
            768: {
                items: 3,
            },
            1024: {
                items: 4,
            }
        }
    });
});