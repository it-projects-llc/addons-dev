odoo.define('openapi.dashboard', function (require) {

    var Widget = require('web.Widget');
    var dashboard = require('web_settings_dashboard');

    dashboard.Dashboard.include({
        init: function(parent, data){
            var ret = this._super(parent, data);
            this.all_dashboards.push('openapi');
            return ret;
        },
        load_openapi: function(data){
            return  new DashboardOpenAPI(this, data.openapi).replace(this.$('.o_web_settings_dashboard_openapi'));
        },
    });

    var DashboardOpenAPI = Widget.extend({

        template: 'DashboardOpenAPI',

        // events: {
        //     'click .o_pay_subscription': 'on_pay_subscription',
        // },

        init: function(parent, data){
            this.data = data;
            this.parent = parent;
            return this._super.apply(this, arguments);
        },

        // on_pay_subscription: function(){

        // },
    });

});
