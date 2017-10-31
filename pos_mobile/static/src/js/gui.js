odoo.define('pos_mobile.gui', function (require) {
    "use strict";

    if (!odoo.is_mobile)
        return;

    var gui = require('point_of_sale.gui');
    var chrome = require('pos_mobile.chrome');

    gui.Gui.include({
        show_screen: function(screen_name,params,refresh,skip_close_popup) {
            this._super(screen_name,params,refresh,skip_close_popup);
            var order = this.pos.get_order();
            if (order) {
                var current_screen_name = order.get_screen_data('screen');
                var swiper_container = $('.swiper-container-v');
                if (current_screen_name === "products") {
                    swiper_container.css({'display': 'block'});
                    $('.pos-content .window').css({'display': 'none'});
                } else {
                    swiper_container.css({'display': 'none'});
                    $('.pos-content .window').css({'display': 'table'});
                }
            }
        }
    });
    return gui;
});
