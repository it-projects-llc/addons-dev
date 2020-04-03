odoo.define('accountReports.FollowupFormView', function (require) {
"use strict";

/**
 * FollowupFormView
 *
 * The FollowupFormView is a sub-view of FormView. It's used to display
 * the Follow-up reports, and manage the complete flow (send by mail, send
 * letter, ...).
 */

var FollowupFormController = require('accountReports.FollowupFormController');
var FollowupFormModel = require('accountReports.FollowupFormModel');
var FollowupFormRenderer = require('accountReports.FollowupFormRenderer');
var FormView = require('web.FormView');
var viewRegistry = require('web.view_registry');

var FollowupFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Controller: FollowupFormController,
        Model: FollowupFormModel,
        Renderer: FollowupFormRenderer,
    }),
    /**
     * This parameter was added in order to display the custom searchview
     * (progress bar) as it is hidden by default on a form view.
     */
    searchable: true,
});

viewRegistry.add('followup_form', FollowupFormView);

return FollowupFormView;
});