/* Copyright 2018 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
   License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_wechat_miniprogram.chrome', function(require){
    "use strict";

    var chrome = require('point_of_sale.chrome');

    chrome.OrderSelectorWidget.include({
        renderElement: function() {
            this._super();
            var order = this.pos.get_order();
            if (order && order.miniprogram_order.state === "done") {
                $(this.el).addClass('paid');
            } else {
                $(this.el).removeClass('paid');
            }
        }
    });

    return chrome;
});
