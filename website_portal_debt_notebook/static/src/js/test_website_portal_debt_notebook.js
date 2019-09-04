/*  Copyright 2019 Anvar Kildebekov <https://it-projects.info/team/fedoranvar>
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('website_portal_debt_notebook.tour', function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var core = require('web.core');
    var base = require("web_editor.base");
    var _t = core._t;

    function check_debt_history(journal, cash) {
        return [{
            trigger: "a[href*='/my/debt_history']:first",
            content: _t("<p>Click to enter 'debt history'</p>"),
            position: "bottom",
        },{
            trigger: ".history-line:nth-child(2)",
            content: _t("<p>Check credit-lines</p>"),
            position: "bottom",
            run: function(){
                for (var i = 0; i < 2; i++) {
                    var line_journal = $(".history-line:nth-child(" + (i+1).toString() + ")>td:nth-child(2)")[0].innerText;
                    var line_cash = $(".history-line:nth-child(" + (i+1).toString() + ")>td:nth-child(4)")[0].innerText;
                    if (line_journal !== journal || line_cash !== cash[i]) {
                        console.log(i + '-line failed: ' + line_journal + ' || ' + line_cash + '\n');
                        console.log('error');
                        break;
                    }
                }
            }
        }];
    }

    var steps = [];
    var journal = "Test (USD)";
    var cash = ["10.0",
                "1.0"];
    steps = steps.concat(check_debt_history(journal, cash));

    tour.register('website_portal_debt_notebook_tour', { test: true, url: '/my', wait_for: base.ready()}, steps);
});
