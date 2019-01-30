odoo.define('odoo_marketplace.tour', function(require) {
"use strict";
 
var core = require('web.core');
var tour = require('web_tour.tour');
 
var _t = core._t;
 
tour.register('marketplace_tour',{url: "/web",},
    [{
        trigger: '.o_app[data-menu-xmlid="odoo_marketplace.wk_seller_dashboard"], .oe_menu_toggler[data-menu-xmlid="odoo_marketplace.wk_seller_dashboard"]',
        content: _t('Manage your marketplace activities from here.'),
        position: 'bottom',
    },
    {
        trigger: '.pending_seller_tooltip',
        content: _t('Visit pending sellers from here.'),
        position: 'left',
    },
    ]);

tour.register('marketplace_tour2',{url: "/web",},
    [{
        trigger: 'li a[data-menu-xmlid="odoo_marketplace.wk_seller_dashboard_menu2_sub_menu0"], div[data-menu-xmlid="odoo_marketplace.wk_seller_dashboard_menu2_sub_menu0"]',
        content: _t('Seller can create new product from here.'),
        position: 'bottom',
    }
    ]);

tour.register('marketplace_tour3',{url: "/web",},
    [{
        trigger: '.pending_product_tooltip',
        content: _t('Visit marketplace pending products from here.'),
        position: 'left',
    }]);

tour.register('marketplace_tour4',{url: "/web",},
    [{
        trigger: 'li a[data-menu-xmlid="odoo_marketplace.wk_seller_dashboard_menu1_sub_menu1"], div[data-menu-xmlid="odoo_marketplace.wk_seller_dashboard_menu1_sub_menu1"]',
        content: _t('Visit all marketplace seller profiles from here.'),
        position: 'bottom',
    },]);
});
