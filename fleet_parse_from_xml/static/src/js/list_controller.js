odoo.define('fleet_parse_from_xml.ListController', function (require) {
"use strict";

var ListController = require('web.ListController');

ListController.include({
    _onCreateRecord: function (event) {
        if (this.modelName !== 'driving.data') {
            this._super(event);
        } else {
            this.do_action({
                type: "ir.actions.act_window",
                name: "Create New Driving Data",
                res_model: "driving.data.wizard",
                views: [[false,'form']],
                target: 'new',
                view_type : 'form',
                view_mode : 'form',
                flags: {
                    'form': {
                        'action_buttons': true,
                        'options': {
                            'mode': 'edit'
                        }
                    }
                }
            });
            return {
                'type': 'ir.actions.client',
//                'tag': 'reload',
            }
        }
    },

});

});
