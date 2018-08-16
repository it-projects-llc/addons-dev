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
    need_control_panel: false,
    jsLibs: [
        '/web/static/lib/nvd3/d3.v3.js',
        '/web/static/lib/nvd3/nv.d3.js',
        '/web/static/src/js/libs/nvd3.js'
    ],
    events: {
        'click .o_dashboard_action_add_database': 'o_dashboard_action_add_database',
        'click .o_dashboard_action_update_info': 'o_dashboard_action_update_info',
        'click .o_dashboard_action_make_backup': 'o_dashboard_action_make_backup',
        'click .o_dashboard_action_up_balance': 'o_dashboard_action_up_balance',
    },

    willStart: function() {
        var self = this;
        return $.when(ajax.loadLibs(this), this._super()).then(function() {
            return self.prepare_dashboard_data();
        });
    },

    start: function() {
        var self = this;
        return this._super().then(function() {
            self.render_dbs();
        });
    },

    prepare_dashboard_data: function() {
        var self = this;
        return $.when(
            self._rpc({
                model: 'odoo_backup_sh.config',
                method: 'search_read',
                fields: ['database', 'active'],
                context: {active_test: false},
            }).done(function(configs) {
                self.configs = configs;
                self.show_nocontent_msg = configs.length === 0;
                self.show_inactive_warning = !self.show_nocontent_msg &&
                    configs.every(function (config) {
                        return !config.active;
                    });
            }),
            self._rpc({
                model: 'odoo_backup_sh.config',
                method: 'get_cloud_params',
                kwargs: {
                    redirect: '/web/backup_redirect?redirect=' + window.location.href,
                },
            }).done(function(cloud_params) {
                if ('auth_link' in cloud_params) {
                    self.do_action({
                        name: "Auth via odoo.com",
                        target: 'self',
                        type: 'ir.actions.act_url',
                        url: cloud_params.auth_link
                    });
                }
                self.cloud_params = cloud_params;
            }),
            self._rpc({
                model: 'odoo_backup_sh.config',
                method: 'check_insufficient_credit',
                kwargs: {
                    credit: 10,
                },
            }).done(function(response) {
                self.show_insufficient_credit_warning = response;
            })
        );
    },

    render_dbs: function() {
        var self = this;
        self.$('.o_backup_dashboard_content').append(QWeb.render('odoo_backup_sh.databases', {dbs: self.configs}));
    },

    o_dashboard_action_add_database: function (ev) {
        ev.preventDefault();
        this.do_action({
            name: "Create backup configuration",
            type: 'ir.actions.act_window',
            view_type: 'form',
            view_mode: 'form',
            views: [[false, "form"]],
            res_model: 'odoo_backup_sh.config',
            target: 'current',
        });
    },

    o_dashboard_action_update_info: function (ev) {
        if (ev) {
            ev.preventDefault();
        }
        var self = this;
        this._rpc({
            model: 'odoo_backup_sh.config',
            method: 'update_info',
            kwargs: {
                cloud_params: self.cloud_params,
            },
        }).then(function (result) {
            if ('reload_page' in result) {
                window.location.reload();
            } else if ('error' in result) {
                self.$('.o_backup_dashboard_note_section').append(
                    QWeb.render('odoo_backup_sh.error_msg', {error_msg: result.error}));
            }
        });
    },

    o_dashboard_action_make_backup: function (ev) {
        ev.preventDefault();
        this._rpc({
            model: 'odoo_backup_sh.config',
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
