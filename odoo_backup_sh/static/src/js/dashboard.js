// Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

odoo.define('odoo_backup_sh.dashboard', function (require) {
'use strict';

var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Widget = require('web.Widget');
var QWeb = core.qweb;

var Dashboard = Widget.extend(ControlPanelMixin, {
    template: 'odoo_backup_sh.BackupDashboardMain',
    events: {
        'click .o_dashboard_action_update_info': 'o_dashboard_action_update_info',
        'click .o_dashboard_action_make_backup': 'o_dashboard_action_make_backup',
        'click .o_dashboard_action_up_balance': 'o_dashboard_action_up_balance',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['odoo_backup_sh.databases'];
    },

    willStart: function() {
        var self = this;
        return $.when(ajax.loadLibs(this), this._super()).then(function() {
            return self.o_dashboard_action_update_info();
        });
    },

    render_dashboards: function() {
        var self = this;
        _.each(this.dashboards_templates, function(template) {
            self.$('.o_backup_dashboard_content').append(QWeb.render(template, {widget: self}));
        });
    },

    o_dashboard_action_update_info: function (ev) {
        if (ev) {
            ev.preventDefault();
        }
        var self = this;
        this._rpc({
            model: 'odoo_backup_sh.dashboard',
            method: 'update_info',
            kwargs: {
                redirect: '/web/backup_redirect?redirect=' + window.location.href,
            },
        }).then(function (result) {
            self.dashboards_data = result;
            if ('backup_list' in result) {
                self.$('.o_backup_dashboard_content').empty();
                self.render_dashboards();
                if ('credit_url' in result) {
                    self.$('#up_to_the_balance_text').hide();
                    self.$('#insufficient_credit_notice').removeClass('hide');
                }
            }
            else if ('auth_link' in result) {
                self.do_action({
                    name: "Auth via odoo.com",
                    target: 'self',
                    type: 'ir.actions.act_url',
                    url: result['auth_link']
                });
            } else if ('reload_page' in result) {
                window.location.reload();
            } else if ('error' in result) {
                console.log('we have got an error: ' + result['error'])
                // TODO: show an error message
            }
        });
    },

    o_dashboard_action_make_backup: function (ev) {
        ev.preventDefault();
        this._rpc({
            model: 'odoo_backup_sh.dashboard',
            method: 'make_backup',
            kwargs: {
                name: $(ev.currentTarget).data('name'),
            },
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
