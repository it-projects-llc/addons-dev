// Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

odoo.define('odoo_backup_sh.dashboard', function (require) {
'use strict';

var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Widget = require('web.Widget');

var Dashboard = Widget.extend(ControlPanelMixin, {
    template: 'odoo_backup_sh.BackupDashboardMain',
    events: {
        'click .o_dashboard_action_update_info': 'o_dashboard_action_update_info',
        'click .o_dashboard_action_make_backup': 'o_dashboard_action_make_backup',
        'click .o_dashboard_action_up_balance': 'o_dashboard_action_up_balance',
    },

    o_dashboard_action_update_info: function (ev) {
        ev.preventDefault();
        var self = this;
        this._rpc({
            model: 'odoo_backup_sh.backup',
            method: 'update_info',
            kwargs: {
                redirect: '/web/backup_redirect?redirect=' + window.location.href,
            },
        }).then(function(response) {
            if ('auth_link' in response) {
                self.do_action({
                    name: "Auth via odoo.com",
                    target: 'self',
                    type: 'ir.actions.act_url',
                    url: response['auth_link']
                });
            } else {
                // TODO: update view of backups in dashboard here
                if ('credit_url' in response) {
                    $('#up_to_the_balance_text').hide();
                    $('#insufficient_credit_notice').removeClass('hide');
                }
            }
        });
    },

    o_dashboard_action_make_backup: function (ev) {
        ev.preventDefault();
        this._rpc({
            model: 'odoo_backup_sh.backup',
            method: 'make_backup',
        });
    },

    o_dashboard_action_up_balance: function (ev) {
        ev.preventDefault();
        this._rpc({
            model: 'odoo_backup_sh.backup',
            method: 'check_insufficient_credit',
            kwargs: {
                credit: 1000000,
            },
        }, {
            async: false,
            success: function(url) {
                window.open(url.result);
            },
        });
    },
});

core.action_registry.add('backup_dashboard', Dashboard);

return Dashboard;
});
