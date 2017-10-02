odoo.define('pos_mobile.screens', function (require) {
    "use strict";
    if (!odoo.is_mobile)
        return;

    var screens = require('point_of_sale.screens');

    screens.ProductScreenWidget.include({
        renderElement: function () {
            this._super.apply(this, arguments);
            this.pos.ready.then(function(){
                var swiper = new Swiper('.swiper-container');
                var elements = $(".swiper-slide");
                var width = elements.css('width');
                width = Number(width.split("px")[0]);

                var screen_width = elements.length * width;

                $(".swiper-slide").css('width')
                $('.pos .screen').css({'width': screen_width + 'px'});

                var rightpane = $(".rightpane tbody");
                var tr = rightpane.find(".header-row");
                tr.detach();
                rightpane.append(tr);
            });
        },
    });
    return screens;
});
