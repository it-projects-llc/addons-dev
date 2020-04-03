odoo.define('accountReports.FollowupFormController', function (require) {
"use strict";

var core = require('web.core');
var FormController = require('web.FormController');

var _t = core._t;
var QWeb = core.qweb;

var FollowupFormController = FormController.extend({
    custom_events: _.extend({}, FormController.prototype.custom_events, {
        expected_date_changed: '_onExpectedDateChanged',
        next_action_date_changed: '_onNextActionDateChanged',
        on_auto_reminder: '_onAutoReminder',
        on_change_block: '_onChangeBlocked',
        on_change_trust: '_onChangeTrust',
        on_manual_reminder: '_onManualReminder',
        on_save_summary: '_onSaveSummary',
        on_trigger_action: '_onTriggerAction'
    }),
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        // force refresh search view on subsequent navigation
        delete this.searchView;
        this.hasSidebar = false;
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    renderButtons: function ($node) {
        this.$buttons = $(QWeb.render("CustomerStatements.buttons", {
            widget: this
        }));
        this.$buttons.on('click',
            '.o_account_reports_followup_print_letter_button',
            this._onPrintLetter.bind(this));
        this.$buttons.on('click',
            '.o_account_reports_followup_send_mail_button',
            this._onSendMail.bind(this));
        this.$buttons.on('click',
            '.o_account_reports_followup_do_it_later_button',
            this._onDoItLater.bind(this));
        this.$buttons.on('click',
            '.o_account_reports_followup_done_button',
            this._onDone.bind(this));
        this.$buttons.appendTo($node);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Check if the follow-up flow is complete (all the follow-up reports are done
     * or skipped). If the flow is complete, display a rainbow man.
     *
     * @private
     */
    _checkDone: function () {
        if (this.model.isJobComplete()){
            var message = _.str.sprintf(_t('You are done with the follow-ups!<br/>You have skipped %s partner(s).'),
                this.model.getSkippedPartners(this.handle));
            this.trigger_up('show_effect', {
                type: 'rainbow_man',
                fadeout: 'no',
                message: message,
            });
        }
    },
    /**
     * Display the done button in the header and remove any mail alert.
     *
     * @private
     */
    _displayDone: function () {
        this.$buttons.find('button.o_account_reports_followup_done_button').show();
        this.renderer.removeMailAlert();
    },
    /**
     * Display the next follow-up.
     *
     * @private
     */
    _displayNextFollowup: function () {
        var currentIndex = this.model.removeCurrentRecord(this.handle);
        var params = {
            limit: 1,
            offset: currentIndex,
        };
        this.update(params);
        this.$buttons.find('button.o_account_reports_followup_done_button').hide();
        this._checkDone();
    },
    /**
     * Remove the highlight on Send Email button.
     *
     * @private
     */
    _removeHighlightEmail: function () {
        this.$buttons.find('button.o_account_reports_followup_send_mail_button')
            .removeClass('btn-primary').addClass('btn-secondary');
    },
    /**
     * Remove the highlight on Print Letter button.
     *
     * @private
     */
    _removeHighlightPrint: function () {
        this.$buttons.find('button.o_account_reports_followup_print_letter_button')
            .removeClass('btn-primary').addClass('btn-secondary');
    },
    /**
     * @override
     * @private
     */
    _update: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self._updateSearchView();
        });
    },
    /**
     * Update the pager with the progress of the follow-ups.
     *
     * @private
     * @override
     */
    _updatePager: function () {
        if (this.pager) {
            var progressInfo = this.model.getProgressInfos();
            this.pager.updateState({
                current_min: progressInfo.currentElementIndex + 1,
                size: progressInfo.numberTodo,
            });
            this.pager.do_toggle(true);
        }
    },
    /**
     * Replace the search view with a progress bar.
     *
     * @private
     */
    _updateSearchView: function () {
        var progressInfo = this.model.getProgressInfos();
        var total = progressInfo.numberDone + progressInfo.numberTodo;
        this.$searchview = $(QWeb.render("CustomerStatements.followupProgressbar", {
            current: progressInfo.numberDone,
            max: progressInfo.numberDone + progressInfo.numberTodo,
            percent: (progressInfo.numberDone / total * 100),
        }));
        this.update_control_panel({
            cp_content: {
                $searchview: this.$searchview,
                // hack to hide the default searchview buttons
                $searchview_buttons: $(),
            }}, {
            clear: false,
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * When click on 'Auto', display the computed date for next action.
     *
     * @private
     */
    _onAutoReminder: function () {
        if (this.model.isAutoReminder(this.handle)) {
            return;
        }
        var date = this.model.setAutoReminder(this.handle);
        this.renderer.renderAutoReminder(date);
    },
    /**
     * When a move line is blocked or unblocked, we have to write it in DB
     * and reload the HTML to update the total due and total overdue.
     *
     * @private
     * @param {OdooEvent} event
     */
    _onChangeBlocked: function (event) {
        var self = this;
        var checkbox = event.data.checkbox;
        var targetID = event.data.targetID;
        this.model.changeBlockedMoveLine(parseInt(targetID), checkbox).then(function () {
            self.reload();
        });
    },
    /**
     * When the trust of a partner is changed, we have to write it in DB.
     *
     * @private
     * @param {OdooEvent} event
     */
    _onChangeTrust: function (event) {
        var self = this;
        var newTrust = event.data.newTrust;
        this.model.changeTrust(this.handle, newTrust).then(function () {
            self.renderer.renderTrust(newTrust);
        });
    },
    /**
     * When the user skip the partner, we have to update the next action
     * date and update the progress and increase the number of
     * follow-ups SKIPPED.
     *
     * @private
     */
    _onDoItLater: function () {
        var self = this;
        this.model.updateNextAction(this.handle).then(function () {
            self.model.increaseNumberSkipped();
            self._displayNextFollowup();
        });
    },
    /**
     * When the user mark as done a customer statement, we have to
     * update the next action date and update the progress,
     * and increase the number of follow-ups DONE.
     *
     * @private
     */
    _onDone: function () {
        var self = this;
        this.model.updateNextAction(this.handle).then(function () {
            self.model.increaseNumberDone();
            self._displayNextFollowup();
        });
    },
    /**
     * Change the payment expected date of an account.move.line.
     *
     * @private
     * @param {OdooEvent} event
     */
    _onExpectedDateChanged: function (event) {
        event.stopPropagation();
        var self = this;
        this.model.changeExpectedDate(this.handle, event.data.moveLineID, event.data.newDate).then(function () {
            self.reload();
        });
    },
    /**
     * When click on 'Manual', show the datepicker to choose a date for the next
     * reminder.
     *
     * @private
     */
    _onManualReminder: function () {
        if (!this.model.isAutoReminder(this.handle)) {
            return;
        }
        this.model.setManualReminder(this.handle);
        this.renderer.renderManualReminder();
    },
    /**
     * When the user changes the next_action_date, save it in the model.
     *
     * @private
     * @param {OdooEvent} event
     */
    _onNextActionDateChanged: function (event) {
        event.stopPropagation();
        this.model.setNextActionDate(this.handle, event.data.newDate);
    },
    /**
     * Print the customer statement.
     *
     * @private
     */
    _onPrintLetter: function () {
        var self = this;
        var partnerID = this.model.get(this.handle, {raw: true}).res_id;
        var records = {
            ids: [partnerID],
        };
        this._rpc({
            model: 'account.followup.report',
            method: 'print_followups',
            args: [records],
        })
        .then(function (result) {
            self.do_action(result);
            self._removeHighlightPrint();
            self._displayDone();
        });
    },
    /**
     * When the user save the summary, we have to write it in DB.
     *
     * @private
     * @param {OdooEvent} event
     */
    _onSaveSummary: function (event) {
        var self = this;
        var text = event.data.text;
        this.model.saveSummary(this.handle, text).then(function (){
            self.renderer.renderSavedSummary(text);
        });
    },
    /**
     * Send the mail server-side.
     *
     * @private
     */
    _onSendMail: function () {
        var self = this;
        var partnerID = this.model.get(this.handle, {raw: true}).res_id;
        this.options = {};
        this.options.partner_id = partnerID;
        this._rpc({
            model: 'account.followup.report',
            method: 'send_email',
            args: [this.options],
        })
        .then(function () {
            self._removeHighlightEmail();
            self._displayDone();
            self.renderer.renderMailAlert();
        });
    },
    /**
     * This method creates an action depending on the name and then executes
     * this action.
     *
     * @private
     * @param {OdooEvent} event
     */
    _onTriggerAction: function (event) {
        event.stopPropagation();
        var actionName = event.data.actionName;
        var action = {
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            target: 'current',
        };
        switch (actionName) {
            case "open_partner_form":
                _.extend(action, {
                    res_model: 'res.partner',
                    res_id: this.model.localData[this.handle].res_id,
                });
                break;
            case "open_invoice":
                _.extend(action, {
                    res_model: 'account.invoice',
                    res_id: event.data.resId,
                    views: [[event.data.view, 'form']],
                });
                break;
            case "open_move":
                _.extend(action, {
                    res_model: 'account.move',
                    res_id: event.data.resId,
                });
                break;
            default:
                action = undefined;
        }
        if (action) {
            this.do_action(action);
        }
    },
});
return FollowupFormController;
});
