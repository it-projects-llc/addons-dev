odoo.define('field_service_dashboard.dashboard', function (require) {
"use strict";


var core = require('web.core');
var viewRegistry = require('web.view_registry');
var rpc = require('web.rpc');
var session = require('web.session');
var KanbanView = require('web.KanbanView');
var KanbanModel = require('web.KanbanModel');
var KanbanRenderer = require('web.KanbanRenderer');
var KanbanController = require('web.KanbanController');

console.log('core', core);
console.log('session', session);
console.log('KanbanView', KanbanView);

var QWeb = core.qweb;
var _t = core._t;
var _lt = core._lt;

var job_count = [];
var customer_job_count = [];
var unassigned_job_count = [];
var rejected_job_count = [];
var my_invoices = [];
var open_invoices = [];
var is_field_service_manager;
var is_field_service_customer;
var is_field_service_serviceman;
var is_field_service_operator;

var FsmDashboardRenderer = KanbanRenderer.extend({
    _notifyTargetChange: function (target_name, value) {
        this.trigger_up('dashboard_edit_target', {
            target_name: target_name,
            target_value: value,
        });
    },
  /**
     * @override
     * @private
     * @returns {Deferred}
     */
    _render: function() {
        var super_render = this._super;
        var self = this;
        return this._super.apply(this, arguments).then(function () {
                    var values = self.state.dashboardValues;
                    rpc.query({
                                model: 'fsm.dashboard',
                                method: 'get_fsm_dashboard_details',
                                args: [],
                            }).then(function(details){
                            is_field_service_manager=details['is_field_service_manager']
                            is_field_service_customer=details['is_field_service_customer']
                            is_field_service_serviceman=details['is_field_service_serviceman']
                            is_field_service_operator=details['is_field_service_operator']
                            var s_dashboard = QWeb.render('field_service_dashboard.fsm_dashboard',{
                                widget: self,
                                show_demo: self.show_demo,
                                values: values,
                                month_date: details['total_job'],
                                customer_invoice_count_id: details['customer_invoice_count_id'],
                                job_count_id: details['job_count_id'],
                                customer_job_count_id: details['customer_job_count_id'],
                                unassigned_job_count_id: details['unassigned_job_count_id'],
                                rejected_job_count_id: details['rejected_job_count_id'],
                                customer_open_invoice_count_id: details['customer_open_invoice_count_id'],
                                is_field_service_manager: is_field_service_manager,
                                is_field_service_customer: is_field_service_customer,
                                is_field_service_serviceman: is_field_service_serviceman,
                                is_field_service_operator: is_field_service_operator,
                            });
                            super_render.call(self);
                            $(s_dashboard).prependTo(self.$el);
                        });
        });
	},
});

var FsmDashboardController = KanbanController.extend({
    events: _.extend({}, KanbanController.prototype.events, {
        'click .btn_action_view_my_job': 'on_dashboard_action_view_my_job_clicked',
		'click .btn_action_view_job': 'on_dashboard_action_view_job_clicked',
		'click .btn_action_my_invoices': 'on_dashboard_action_my_invoices_clicked',
		'click .btn_action_view_unassigned_job': 'on_dashboard_action_view_unassigned_job_clicked',
		'click .btn_action_view_rejected_job': 'on_dashboard_action_view_rejected_job_clicked',
		'click .btn_action_open_invoices': 'on_dashboard_action_open_invoices_clicked',
    }),

    on_dashboard_action_view_my_job_clicked: function(ev){
		ev.preventDefault();
		this.do_action('field_service_management.action_view_my_job',{});
	},
    on_dashboard_action_view_job_clicked: function(ev){
		ev.preventDefault();
		this.do_action('field_service_management.action_view_job',{});
	},
	on_dashboard_action_view_unassigned_job_clicked: function(ev){
		ev.preventDefault();
		this.do_action('field_service_management.action_view_unassigned_job',{});
	},
	on_dashboard_action_view_rejected_job_clicked: function(ev){
		ev.preventDefault();
		this.do_action('field_service_management.action_view_rejected_job',{});
	},
	on_dashboard_action_my_invoices_clicked: function(ev){
		ev.preventDefault();
		this.do_action({
			name: "My Invoices",
			res_model: 'account.invoice',
			views: [[false, 'list'],
					[false, 'form'],
					[false, 'kanban'],
					],
			type: 'ir.actions.act_window',
			view_type: "list",
			view_mode: "list",
		});
	},
	on_dashboard_action_open_invoices_clicked: function(ev){
		ev.preventDefault();
		this.do_action({
			name: "Open Invoices",
			res_model: 'account.invoice',
			views: [[false, 'list'],
					[false, 'form'],
					[false, 'kanban'],
					],
			type: 'ir.actions.act_window',
			view_type: "list",
			view_mode: "list",
		});
	},
});

var FsmDashboardModel = KanbanModel.extend({
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    init: function () {
        this.dashboardValues = {};
        this._super.apply(this, arguments);
    },

    /**
     * @override
     */
    get: function (localID) {
        var result = this._super.apply(this, arguments);
        if (this.dashboardValues[localID]) {
            result.dashboardValues = this.dashboardValues[localID];
        }
        return result;
    },


    /**
     * @œverride
     * @returns {Deferred}
     */
    load: function () {
        return this._loadDashboard(this._super.apply(this, arguments));
    },
    /**
     * @œverride
     * @returns {Deferred}
     */
    reload: function () {
        return this._loadDashboard(this._super.apply(this, arguments));
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @abstract
     * @returns {Deferred<Object>} resolves to the required dashboard data
     */
    _fetchDashboardData: function () {
        return $.when(this._rpc({
                    model: 'fsm.dashboard',
                    method: 'get_fsm_dashboard_details',
                    args: [],
                }));
    },
    /**
     * @private
     * @param {Deferred} super_def a deferred that resolves with a dataPoint id
     * @returns {Deferred<string>} resolves to the dataPoint id
     */
    _loadDashboard: function (super_def) {
        var self = this;
        var dashboard_def = this._fetchDashboardData();
        return $.when(super_def, dashboard_def).then(function (id, dashboardValues) {
            self.dashboardValues[id] = dashboardValues;
            return id;
        });
    },
});

var FsmDashboardView = KanbanView.extend({
    config: _.extend({}, KanbanView.prototype.config, {
        Model: FsmDashboardModel,
        Renderer: FsmDashboardRenderer,
        Controller: FsmDashboardController,
    }),
    display_name: _lt('Dashboard'),
    icon: 'fa-dashboard',
    searchview_hidden: true,
    template: 'field_service_dashboard.fsm_dashboard',
});
viewRegistry.add('field_service_dashboard_view', FsmDashboardView);
return {
    Model: FsmDashboardModel,
    Renderer: FsmDashboardRenderer,
    Controller: FsmDashboardController,
};
});
