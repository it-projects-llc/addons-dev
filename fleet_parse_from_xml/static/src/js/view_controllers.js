odoo.define('fleet_parse_from_xml.ListController', function (require) {
"use strict";

var ListController = require('web.ListController');
var FormController = require('web.FormController');

ListController.include({
    _onCreateRecord: function (event) {
        if (this.modelName !== 'driving.data') {
            return this._super(event);
        }
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
        };
    },
});

FormController.include({
    _onCreate: function (event) {
        if (this.modelName !== 'driving.data') {
            return this._super(event);
        }
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
        };
    },
});

});
