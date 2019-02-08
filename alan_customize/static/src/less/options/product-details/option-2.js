$(document).ready(function() {
      $('.thumbnails-slides').owlCarousel({
              margin: 10,
              nav:true,
              dots:false
              responsive: {
                  0: {
                      items: 1,
                  },
                  481: {
                      items: 4,
                  },
                  768: {
                      items: 3,
                  },
                  1024: {
                      items: 5,
                  }
              }
      });
});