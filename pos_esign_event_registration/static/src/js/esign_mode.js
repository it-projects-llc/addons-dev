/*  Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_esign_event_registration.esign_mode', function (require) {
"use strict";

var esign_mode = require('pos_esign_request.esign_mode');

esign_mode.AcceptModalKiosk.include({
    compose_vals: function() {
        var res = this._super();
        res.attendee_id = this.kiosk.partner.attendee_id;
        return res;
    },
})

});
