// Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

odoo.define("odoo_backup_sh.tour", function (require) {
    "use strict";

    var core = require("web.core");
    var tour = require("web_tour.tour");

    var _t = core._t;

    tour.register("odoo_backup_sh_tour", {
            url: "/web",
        },
        [
            {
                trigger: '.o_app[data-menu-xmlid="odoo_backup_sh.menu_backup_root"], .oe_menu_toggler[data-menu-xmlid="odoo_backup_sh.menu_backup_root"]',
                content: _t('Want a better way to <b>manage your databases backups</b>? <i>It starts here.</i>'),
                position: "bottom",
            },
            {
                trigger: '.o_dashboard_action_update_info',
                content: _t('Let\'s update information about your backups.'),
                position: "bottom",
            },
            {
                // This step have been added to make sure that the notice on the "Go to Balance" button was shown.
                trigger: '#insufficient_credit_notice',
                run: function () {},
            }
        ]
    );
});
