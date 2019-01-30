// Copyright 2018 Stanislav Krotov <https://it-projects.info/team/ufaks>
// License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

odoo.define('odoo_backup_sh.dashboard', function (require) {
'use strict';

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Widget = require('web.Widget');
var QWeb = core.qweb;

var Dashboard = AbstractAction.extend(ControlPanelMixin, {
    template: 'odoo_backup_sh.BackupDashboardMain',
    need_control_panel: false,
    cssLibs: [
        '/web/static/lib/nvd3/nv.d3.css'
    ],
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
        'click .o_dashboard_action_view_backups': 'o_dashboard_action_view_backups',
        'click .o_backup_dashboard_notification .close': 'close_dashboard_notification',
    },

    willStart: function() {
        var self = this;
        return $.when(ajax.loadLibs(this), this._super()).then(function() {
            return self.fetch_dashboard_data();
        });
    },

    fetch_dashboard_data: function() {
        var self = this;
        return $.when(
            self._rpc({
                route: '/odoo_backup_sh/fetch_dashboard_data',
            }).done(function(results) {
                self.remote_storage_usage_graph_values = results.remote_storage_usage_graph_values;
                self.configs = results.configs;
                self.notifications = results.notifications;
                self.show_nocontent_msg = results.configs.length === 0;
                self.show_inactive_warning = !self.show_nocontent_msg &&
                    results.configs.every(function (config) {
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
            })
        );
    },

    start: function() {
        var self = this;
        return this._super().then(function() {
            if (!self.show_nocontent_msg) {
                self.render_remote_storage_usage_graph();
            }
            self.render_backup_config_cards();
        });
    },

    render_remote_storage_usage_graph: function() {
        var chart_values = this.remote_storage_usage_graph_values;
        var self = this;

        nv.addGraph(function() {
            var chart = nv.models.lineChart()
                .x(function(d) {
                    return self.getDate(d);
                })
                .y(function(d) {
                    return self.getValue(d);
                })
                .forceY([0])
                .useInteractiveGuideline(true)
                .showLegend(false)
                .showYAxis(true)
                .showXAxis(true);
            var tick_values = self.getPrunedTickValues(chart_values[0].values, 5);

            chart.xAxis
                .tickFormat(function(d) {
                    return d3.time.format("%m/%d/%y")(new Date(d));
                })
                .tickValues(_.map(tick_values, function(d) {
                    return self.getDate(d);
                }))
                .rotateLabels(-45);

            chart.yAxis
                .axisLabel('Usage Value, MB')
                .tickFormat(d3.format('.02f'));

            d3.select('#graph_remote_storage_usage')
                .append("svg")
                .attr("height", '24em')
                .datum(chart_values)
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });
    },

    render_backup_config_cards: function() {
        var self = this;
        var $o_backup_dashboard_configs = self.$('.o_backup_dashboard_configs').append(
            QWeb.render('odoo_backup_sh.config_cards', {configs: self.configs}));
        _.each($o_backup_dashboard_configs.find('.o_kanban_record'), function(record) {
            self.render_backup_config_card_graph(record.dataset.db_name);
        });
    },

    render_backup_config_card_graph: function(db_name) {
        var chart_values = this.configs.filter(function (config) {
            return config.database === db_name;
        })[0].graph;

        nv.addGraph(function() {
            var chart = nv.models.discreteBarChart()
                .x(function(d) { return d.label; })
                .y(function(d) { return d.value; })
                .showValues(true)
                .showYAxis(false)
                .color(['#7c7bad'])
                .margin({'left': 0, 'right': 0, 'top': 12, 'bottom': 20});

            d3.select('div[data-db_name="' + db_name + '"] .backup_config_card_graph')
                .append("svg")
                .attr("height", '10em')
                .datum(chart_values)
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });
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
        if (ev && ev.preventDefault) {
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
            }
            $.when(self.fetch_dashboard_data()).then(function() {
                self.$('#graph_remote_storage_usage').empty();
                self.$('.o_backup_dashboard_configs').empty();
                self.start();
            });
        });
    },

    o_dashboard_action_make_backup: function (ev) {
        ev.preventDefault();
        var self = this;
        this._rpc({
            model: 'odoo_backup_sh.config',
            method: 'make_backup',
            kwargs: {
                name: $(ev.currentTarget).closest('div[data-db_name]').data('db_name'),
            },
        }).then(function (result) {
            if (typeof result !== undefined && 'reload_page' in result) {
                window.location.reload();
            }
            self.o_dashboard_action_update_info(self.cloud_params);
        });
    },

    o_dashboard_action_view_backups: function (ev) {
        ev.preventDefault();
        this.do_action({
            name: "Backups",
            type: 'ir.actions.act_window',
            views: [[false, 'list'], [false, 'form']],
            res_model: 'odoo_backup_sh.backup_info',
            target: 'current',
            domain: [['database', '=', $(ev.currentTarget).closest('div[data-db_name]').data('db_name')]],
        });
    },

    o_dashboard_action_up_balance: function (ev) {
        ev.preventDefault();
        this._rpc({
            model: 'odoo_backup_sh.config',
            method: 'get_credit_url',
        }, {
            async: false,
            success: function(url) {
                window.open(url.result);
            },
        });
    },

    close_dashboard_notification: function (ev) {
        ev.preventDefault();
        var $o_backup_dashboard_notification = $(ev.currentTarget).closest('.o_backup_dashboard_notification');
        this._rpc({
            model: 'odoo_backup_sh.notification',
            method: 'toggle_is_read',
            args: [$o_backup_dashboard_notification.data('notification_id')]
        }).then(function () {
            $o_backup_dashboard_notification.hide();
        });
    },

    // Utility functions
    getDate: function(d) { return new Date(d[0]); },
    getValue: function(d) { return d[1]; },
    getPrunedTickValues: function(ticks, nb_desired_ticks) {
        var nb_values = ticks.length;
        var keep_one_of = Math.max(1, Math.floor(nb_values / nb_desired_ticks));

        return _.filter(ticks, function(d, i) {
            return i % keep_one_of === 0;
        });
    },
});

core.action_registry.add('backup_dashboard', Dashboard);

return Dashboard;
});
