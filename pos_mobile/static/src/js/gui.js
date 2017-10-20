odoo.define('pos_mobile.gui', function (require) {
    "use strict";

    if (!odoo.is_mobile)
        return;

    var gui = require('point_of_sale.gui');
    var chrome = require('pos_mobile.chrome');

    gui.Gui.include({
        show_screen: function(screen_name,params,refresh,skip_close_popup) {
            this._super(screen_name,params,refresh,skip_close_popup);
            if (screen_name === "products") {
                $('.swiper-container-v').css({'display': 'block'});
            }
        }
    });
});
