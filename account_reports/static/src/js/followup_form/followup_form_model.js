odoo.define('accountReports.FollowupFormModel', function (require) {
"use strict";

var BasicModel = require('web.BasicModel');
var field_utils = require('web.field_utils');
var session = require('web.session');

var FollowupFormModel = BasicModel.extend({
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        // Number of Follow-ups DONE
        this.numberDone = undefined;
        // Number of Follow-ups REMAINING
        this.numberTodo = undefined;
        // Number of Follow-ups SKIPPED
        this.numberSkipped = undefined;
        this.currentElementIndex = undefined;
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Set the blocked status of an account.move.line and save in DB.
     *
     * @param {Integer} moveLineID id of the account.move.line
     * @param {boolean} blocked true if the account.move.line is blocked,
     *                          false otherwise
     * @return {Deferred}
     */
    changeBlockedMoveLine: function (moveLineID, blocked) {
        return this._rpc({
            model: 'account.move.line',
            method: 'write_blocked',
            args: [[moveLineID], blocked]
        });
    },
    /**
     * Set the payment expected date of an account.move.line and save in DB.
     *
     * @param {string} handle Local resource id of a record
     * @param {Integer} moveLineID id of the account.move.line
     * @param {Moment} date Expected date
     * @return {Deferred}
     */
    changeExpectedDate: function (handle, moveLineID, date) {
        return this._rpc({
            model: 'res.partner',
            method: 'change_expected_date',
            args: [[this.localData[handle].res_id], {
                move_line_id: moveLineID,
                expected_pay_date: date
            }],
        });
    },
    /**
     * Change the trust of a partner and save in DB.
     *
     * @param {string} handle Local resource id of a record
     * @param {string} newTrust new trust for the partner (good, normal or bad)
     * @return {Deferred}
     */
    changeTrust: function (handle, newTrust) {
        return this._rpc({
            model: 'res.partner',
            method: 'write',
            args: [[this.localData[handle].res_id], {trust: newTrust}],
        });
    },
    /**
     * Get the informations about the flow of follow-ups.
     *
     * @return {Object} Informations about the progress of the job
     */
    getProgressInfos: function () {
        return {
            numberDone: this.numberDone,
            numberTodo: this.numberTodo,
            currentElementIndex: this.currentElementIndex
        };
    },
    /**
     *
     * @return {Integer} number of skipped partners
     */
    getSkippedPartners: function () {
        return this.numberSkipped;
    },
    increaseNumberDone: function () {
        this.numberDone++;
    },
    increaseNumberSkipped: function () {
        this.numberSkipped++;
    },
    /**
     * @param {string} handle Local resource id of a record
     * @return {boolean} true if the next_action is set to 'auto',
     *                   false otherwise
     */
    isAutoReminder: function (handle) {
        return this.localData[handle].data.next_action === 'auto';
    },
    /**
     * @return {boolean} true is all followups are done or skipped.
     */
    isJobComplete: function () {
        return this.numberTodo === 0;
    },
    /**
     * @override
     */
    load: function (params) {
        var self = this;
        this.modelName = params.modelName;
        this._computeProgressBar(params.res_id, params.res_ids);
        return this._super(params).then(function (id){
            return self._fetch(id);
        });
    },
    /**
     * @override
     */
    reload: function (handle, params) {
        if (params.offset !== undefined || params.currentId !== undefined) {
            this.localData[handle].data.report_manager_id = undefined;
        }
        if (params.offset !== undefined) {
            this.currentElementIndex = params.offset;
        }
        if (params.ids !== undefined && params.currentId !== undefined) {
            this._computeProgressBar(params.currentId, params.ids);
        }
        var self = this;
        return this._super(handle, params).then(function (id){
            return self._fetch(id);
        });
    },
    /**
     * Remove the current record from the localData, and return the index of the
     * next record.
     *
     * @param {string} handle Local resource id of a record
     * @return {integer} index of the next record
     */
    removeCurrentRecord: function (handle) {
        this.numberTodo--;
        var index = this.localData[handle].res_ids.indexOf(this.localData[handle].res_id);
        this.localData[handle].res_ids.splice(index, 1);
        if (this.currentElementIndex >= this.localData[handle].res_ids.length) {
            this.currentElementIndex = this.localData[handle].res_ids.length-1;
        }
        return this.currentElementIndex;
    },
    /**
     * Save the summary, and save it in DB.
     *
     * @param {string} handle Local resource id of a record
     * @param {string} text new summary
     * @return {Deferred}
     */
    saveSummary: function (handle, text) {
        return this._rpc({
            model: 'account.report.manager',
            method: 'write',
            args: [this.localData[handle].data.report_manager_id, {summary: text}],
        });
    },
    /**
     * Set the next_action in 'auto' mode.
     *
     * @param {string} handle Local resource id of a record
     * @return {string} date of next action
     */
    setAutoReminder: function (handle) {
        var data = this.localData[handle].data;
        data.next_action = 'auto';
        data.next_action_date = data.next_action_date_auto;
        return data.next_action_date_auto;
    },
    /**
     * Set the next_action in 'manual' mode.
     *
     * @param {string} handle Local resource id of a record
     */
    setManualReminder: function (handle) {
        this.localData[handle].data.next_action = 'manual';
    },
    /**
     *
     * @param {string} handle Local resource id of a record
     * @param {string} date Date of next action
     */
    setNextActionDate: function (handle, date) {
        this.localData[handle].data.next_action_date = date;
    },
    /**
     * Update the date of next action.
     *
     * @param {string} handle Local resource id of a record
     * @return {Deferred}
     */
    updateNextAction: function (handle) {
        var record = this.localData[handle];
        var next_action_date = field_utils.parse.date(record.data.next_action_date, {}, {isUTC: true});
        return this._rpc({
            model: 'res.partner',
            method: 'update_next_action',
            args: [[record.res_id], {
                next_action_type: record.data.next_action,
                next_action_date: next_action_date
            }],
        });
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Compute the number of records for the progressBar and the pager.
     *
     * @private
     * @param {string} id id for the local resource
     * @param {Array} records list of all ids
     */
    _computeProgressBar: function (id, records) {
        this.numberTodo = records.length;
        this.currentElementIndex = records.indexOf(id);
        this.numberDone = 0;
        this.numberSkipped = 0;
    },
    /**
     * Fetch the html of the followup.
     *
     * @private
     * @param {string} id id for the local resource
     * @returns {Deferred<string>} local id of the record
     */
    _fetch: function (id) {
        var self = this;
        var params = {};
        if (this.localData[id].data.report_manager_id !== undefined) {
            params.keep_summary = true;
        }
        return this._rpc({
            model: 'account.followup.report',
            method: 'get_followup_informations',
            args: [this.localData[id].res_id, params],
            kwargs: {context: session.user_context},
        }).then(function (data) {
            self.localData[id].data.report_manager_id = data.report_manager_id;
            self.localData[id].data.followup_html = data.html;
            if (data.next_action) {
                self.localData[id].data.next_action = data.next_action.type;
                self.localData[id].data.next_action_date = data.next_action.date;
                self.localData[id].data.next_action_date_auto = data.next_action.date_auto;
            }
            return self.localData[id].id;
        });
    },
});
return FollowupFormModel;
});
