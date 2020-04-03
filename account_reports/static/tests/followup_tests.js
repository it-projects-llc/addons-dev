odoo.define('accountReports.FollowupTests', function (require) {
"use strict";

var FollowupFormView = require('accountReports.FollowupFormView');
var testUtils = require('web.test_utils');

var createView = testUtils.createView;

QUnit.module('FollowupViews', {
    beforeEach: function () {
        this.data = {
            res_partner: {
                fields: {
                    id: {string: "ID", type: "integer"},
                },
                records: [
                    {
                        id: 9,
                    },
                ]
            },
        };
    }
}, function () {

    QUnit.module('FollowupFormView');

    QUnit.test('followup form view get_followup_informations', function (assert) {
        assert.expect(2);

        var followupFormView = createView({
            View: FollowupFormView,
            model: 'res_partner',
            data: this.data,
            arch: '<form><sheet><followup/></sheet></form>',
            res_id: 9,
            res_ids: [9],
            mockRPC: function (route, args) {
                if (args.method === 'get_followup_informations') {
                    assert.strictEqual(args.args[0], 9, "followup form view should call 'get_followup_informations' with id=9");
                    return $.when({
                        report_manager_id: 1,
                        next_action: {
                            type: 'auto',
                            date_auto: '09/10/2017'
                        },
                        html: '<div class="o_account_reports_body"><div class="container o_account_reports_page o_account_reports_no_print"></div></div>'
                    });
                }
                return this._super.apply(this, arguments);
            },
        });
        assert.strictEqual(followupFormView.$('div.o_account_reports_body').length, 1, "Html content should be rendered");

        followupFormView.destroy();
    });

    QUnit.test('followup form view do it later', function (assert) {
        assert.expect(7);

        var followupFormView = createView({
            View: FollowupFormView,
            model: 'res_partner',
            data: this.data,
            arch: '<form js_class="followup_form"><sheet><followup/></sheet></form>',
            res_id: 9,
            res_ids: [9],
            mockRPC: function (route, args) {
                if (args.method === 'update_next_action') {
                    assert.strictEqual(args.args[0][0], 9, "followup form view should call 'update_next_action' with id=9");
                    assert.strictEqual(args.args[1].next_action_type, 'auto', "followup form view should call 'update_next_action' with next_action_type = auto");
                    return $.when();
                }
                if (args.method === 'get_followup_informations') {
                    return $.when({
                        report_manager_id: 1,
                        next_action: {
                            type: 'auto',
                            date_auto: '09/10/2017'
                        },
                        html: '<div class="o_account_reports_body"><div class="container o_account_reports_page o_account_reports_no_print"></div></div>'
                    });
                }
                return this._super.apply(this, arguments);
            },
        });

        var $buttons = followupFormView.$buttons;
        var $buttonDoItLater = $buttons.find('button.o_account_reports_followup_do_it_later_button');
        var $buttonDone = $buttons.find('button.o_account_reports_followup_done_button');
        assert.ok($buttonDoItLater.hasClass('btn-secondary'),
            "Do It Later button should have class 'btn-secondary'");
        assert.strictEqual($buttonDone.css('display'), 'none',
            "Done button should be invisible");
        assert.ok(followupFormView.$searchview.is(':visible'),
            "The custom searchview should be visible on the form");
        assert.strictEqual(followupFormView.$searchview.find('span.o_account-progress-bar-content').text(), '0/1',
            "Progress bar value should be '0/1'");
        $buttonDoItLater.click();

        assert.strictEqual(followupFormView.$searchview.find('span.o_account-progress-bar-content').text(), '0/0',
            "Progress bar value should be '0/0' after click on 'Do It Later'");

        followupFormView.destroy();
    });

    QUnit.test('followup form print letter', function (assert) {
        assert.expect(7);

        var followupFormView = createView({
            View: FollowupFormView,
            model: 'res_partner',
            data: this.data,
            arch: '<form js_class="followup_form"><sheet><followup/></sheet></form>',
            res_id: 9,
            res_ids: [9],
            mockRPC: function (route, args) {
                if (args.method === 'get_followup_informations') {
                    return $.when({
                        report_manager_id: 1,
                        next_action: {
                            type: 'auto',
                            date_auto: '09/10/2017'
                        },
                        html: '<div class="o_account_reports_body"><div class="container o_account_reports_page o_account_reports_no_print"></div></div>'
                    });
                }
                if (args.method === 'print_followups') {
                    assert.ok(true, "Should call 'print_followups' route");
                    return $.when({});
                }
                if (args.method === 'update_next_action') {
                    assert.ok(true, "Should call 'update_next_action' route when click on done");
                    return $.when({});
                }
                return this._super.apply(this, arguments);
            },
        });

        var $buttonPrintLetter = followupFormView.$buttons.find('button.o_account_reports_followup_print_letter_button');
        assert.strictEqual(followupFormView.$buttons.find('button.o_account_reports_followup_done_button').css('display'), 'none',
            "Done button should be invisible");

        $buttonPrintLetter.click();

        assert.strictEqual(followupFormView.$searchview.find('span.o_account-progress-bar-content').text(), '0/1',
            "Progress bar value should be '0/1'");

        assert.strictEqual(followupFormView.$buttons.find('button.o_account_reports_followup_done_button').css('display'), 'inline-block',
            "Done button should be visible after print");

        followupFormView.$buttons.find('button.o_account_reports_followup_done_button').click();

        assert.strictEqual(followupFormView.$searchview.find('span.o_account-progress-bar-content').text(), '1/1',
            "Progress bar value should be '1/1' after done");

        assert.strictEqual(followupFormView.$buttons.find('button.o_account_reports_followup_done_button').css('display'), 'none',
            "Done button should be invisible after done");

        followupFormView.destroy();
    });

    QUnit.test('followup form view multiple records', function (assert) {
        assert.expect(6);

        this.data.res_partner.records = [{id: 9}, {id: 10}, {id: 11}, {id: 12}];

        var followupFormView = createView({
            View: FollowupFormView,
            model: 'res_partner',
            data: this.data,
            arch: '<form><sheet><followup/></sheet></form>',
            res_id: 9,
            viewOptions: {
                ids: [9, 10, 11, 12],
                index: 0,
            },
            mockRPC: function (route, args) {
                if (args.method === 'update_next_action') {
                    return $.when();
                }
                if (args.method === 'get_followup_informations') {
                    return $.when({
                        report_manager_id: 1,
                        next_action: {
                            type: 'auto',
                            date_auto: '09/10/2017'
                        },
                        html: '<div class="o_account_reports_body"><div class="container o_account_reports_page o_account_reports_no_print"></div></div>'
                    });
                }
                return this._super.apply(this, arguments);
            },
        });
        assert.strictEqual(followupFormView.$searchview.find('span.o_account-progress-bar-content').text(), '0/4',
            "Progress bar value should be '0/4'");
        assert.strictEqual(followupFormView.pager.$('.o_pager_value').text(), "1", 'pager value should be 1');
        assert.strictEqual(followupFormView.pager.$('.o_pager_limit').text(), "4", 'pager limit should be 4');
        followupFormView.pager.$('.o_pager_next').click();

        assert.strictEqual(followupFormView.pager.$('.o_pager_value').text(), "2", 'pager value should be 2');

        var $buttonDoItLater = followupFormView.$buttons.find('button.o_account_reports_followup_do_it_later_button');
        $buttonDoItLater.click();

        assert.strictEqual(followupFormView.pager.$('.o_pager_value').text(), "2", 'pager value should be 2');
        assert.strictEqual(followupFormView.pager.$('.o_pager_limit').text(), "3", 'pager limit should be 3');

        followupFormView.destroy();
    });

});
});
