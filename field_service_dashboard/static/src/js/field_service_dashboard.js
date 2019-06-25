odoo.define('field_service_dashboard.dashboard', function (require) {
"use strict";

var core = require('web.core');
var formats = require('web.formats');
var Model = require('web.Model');
var session = require('web.session');
var KanbanView = require('web_kanban.KanbanView');

console.log('core', core)
console.log('formats', formats)
console.log('Model', Model)
console.log('session', session)
console.log('KanbanView', KanbanView)

var QWeb = core.qweb;
var _t = core._t;
var _lt = core._lt;

var job_count = []
var customer_job_count = []
var unassigned_job_count = []
var rejected_job_count = []
var my_invoices = []
var open_invoices = []
var is_field_service_manager
var is_field_service_customer
var is_field_service_serviceman
var is_field_service_operator
var FsmDashboardView = KanbanView.extend({
	display_name: _lt('Dashboard'),
	icon: 'fa-dashboard',
	view_type: "field_service_dashboard_view",
	searchview_hidden: true,
	events: {
		'click .btn_action_view_my_job': 'on_dashboard_action_view_my_job_clicked',
		'click .btn_action_view_job': 'on_dashboard_action_view_job_clicked',
		'click .btn_action_my_invoices': 'on_dashboard_action_my_invoices_clicked',
		'click .btn_action_view_unassigned_job': 'on_dashboard_action_view_unassigned_job_clicked',
		'click .btn_action_view_rejected_job': 'on_dashboard_action_view_rejected_job_clicked',
		'click .btn_action_open_invoices': 'on_dashboard_action_open_invoices_clicked',
	},
	fetch_data: function() {
		// Overwrite this function with useful data
		return $.when();
	},
		render: function() {
		var super_render = this._super;
		var self = this;
		return this.fetch_data().then(function(result){
			self.show_demo = result && result.nb_opportunities === 0;
			var employee = new Model('fsm.dashboard')
						.call('get_fsm_dashboard_details').then(function(details){
							is_field_service_manager=details['is_field_service_manager']
							is_field_service_customer=details['is_field_service_customer']
							is_field_service_serviceman=details['is_field_service_serviceman']
							is_field_service_operator=details['is_field_service_operator']
							var s_dashboard = QWeb.render('field_service_dashboard.fsm_dashboard',{
								widget: self,
								show_demo: self.show_demo,
								values: result,
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
core.view_registry.add('field_service_dashboard_view', FsmDashboardView);
return FsmDashboardView;
});
