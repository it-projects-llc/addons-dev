/* Copyright 2017 Openworx.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define('backend_theme_v10.sidebar-toggle', function (require) {
    "use strict";
    
    var session = require('web.session');
    var rpc = require('web.rpc');
    
    var id = session.uid;

    var domain = [['id', '=', id]];
    var fields = ['sidebar_visible'];
    rpc.query({
                model: 'res.users',
                method: 'search_read',
                args: [domain, fields],
            }).then(function(res) {
                    var toggle = res[0]['sidebar_visible'];
                    if (toggle === true) {
                        $("#app-sidebar").removeClass("toggle-sidebar");
                    } else {
                        $("#app-sidebar").addClass("toggle-sidebar");
                    };
                });
});
