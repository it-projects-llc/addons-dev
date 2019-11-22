/* Copyright 2017 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */

odoo.define('pos_durak.tour', function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var core = require('web.core');
    var _t = core._t;

    var steps = [tour.STEPS.SHOW_APPS_MENU_ITEM, {
        trigger: '.o_app[data-menu-xmlid="point_of_sale.menu_point_root"]',
        content: _t("Ready to launch your <b>point of sale</b>? <i>Click here</i>."),
        position: 'right',
        edition: 'community'
    }, {
        trigger: '.o_app[data-menu-xmlid="point_of_sale.menu_point_root"]',
        content: _t("Ready to launch your <b>point of sale</b>? <i>Click here</i>."),
        position: 'bottom',
        edition: 'enterprise'
    }, {
        trigger: ".o_pos_kanban :has(div.o_primary:contains('Shop')) button.oe_kanban_action_button",
        content: _t("<p>Click to start the point of sale interface. It <b>runs on tablets</b>, laptops, or industrial hardware.</p><p>Once the session launched, the system continues to run without an internet connection.</p>"),
        position: "bottom"
    },{
        trigger: ".fa-list-alt",
        content: _t("<p>Click to start the point of sale interface. It <b>runs on tablets</b>, laptops, or industrial hardware.</p><p>Once the session launched, the system continues to run without an internet connection.</p>"),
        position: "bottom"
    }];

    tour.register('tour_pos_durak', { test: true, url: '/web' }, steps);
});
