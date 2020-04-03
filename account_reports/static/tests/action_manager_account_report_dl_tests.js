odoo.define('account_reports.account_reports_tests', function (require) {
"use strict";

var testUtils = require('web.test_utils');

var createActionManager = testUtils.createActionManager;

QUnit.module('Account Reports', {
    beforeEach: function () {
        this.actions = [{
            id: 1,
            data: {
                model: 'some_model',
                options: {
                    someOption: true,
                },
                output_format: 'pdf',
            },
            type: 'ir_actions_account_report_download',
        }];
    },
}, function () {

    QUnit.test('can execute account report download actions', function (assert) {
        assert.expect(5);

        var actionManager = createActionManager({
            actions: this.actions,
            mockRPC: function (route, args) {
                assert.step(args.method || route);
                return this._super.apply(this, arguments);
            },
            session: {
                get_file: function (params) {
                    assert.step(params.url);
                    assert.deepEqual(params.data, {
                        model: 'some_model',
                        options: {
                            someOption: true,
                        },
                        output_format: 'pdf',
                    }, "should give the correct data");
                    params.complete();
                },
            },
        });
        actionManager.doAction(1);

        assert.verifySteps([
            '/web/action/load',
            '/web/static/src/img/spin.png', // block UI image
            '/account_reports',
        ]);

        actionManager.destroy();
    });

    QUnit.test('Account report m2m filters', function (assert) {
        assert.expect(4);
        var count = 0;
        var actionManager = createActionManager({
            actions: [{
                id: 9,
                tag: 'account_report',
                type: 'ir.actions.client',
            }],
            data: {
                'res.partner.category': {
                    fields: {
                        display_name: { string: "Displayed name", type: "char" },
                    },
                    records: [{
                        id: 1,
                        display_name: "Brigadier suryadev singh",
                    }],
                },
                'res.partner': {
                    fields: {
                        display_name: { string: "Displayed name", type: "char" },
                        partner_ids: {string: "Partner", type: "many2many", relation: 'partner'},
                    },
                    records: [{
                        id: 1,
                        display_name: "Genda Swami",
                        partner_ids: [1],
                    }]
                },
            },
            mockRPC: function (route, args) {
                if (route === '/web/dataset/call_kw/account.report/get_report_informations') {
                    var vals = {
                        options: {partner: true, partner_ids: [], partner_categories:[]},
                        buttons: [],
                        searchview_html: '<a class="dropdown-toggle" data-toggle="dropdown">' +
                            '<span class="fa fa-folder-open"/> Partners' +
                            '<span class="caret" />' +
                            '</a>' +
                            '<ul class="dropdown-menu o_filters_menu" role="menu">' +
                            '<li class="o_account_report_search js_account_partner_m2m"/>' +
                            '</ul>',
                    };
                    if (count === 1) {
                        var reportOptions = args.args[1];
                        assert.strictEqual(reportOptions.partner_ids[0], 1,
                            "pass correct partner_id to report");
                        vals.options.partner_ids = reportOptions.partner_ids;
                    } else if (count == 2) {
                        var reportOptions = args.args[1];
                        assert.strictEqual(reportOptions.partner_categories[0], 1,
                            "pass correct partner_id to report");
                        vals.options.partner_categories = reportOptions.partner_categories;
                    }
                    count++;
                    return $.when(vals);
                }
                if (route === '/web/dataset/call_kw/account.report/get_html_footnotes') {
                    return $.when("");
                }
                return this._super.apply(this, arguments);
            },
        });

        actionManager.doAction(9);
        assert.strictEqual(actionManager.controlPanel.$('.o_field_many2manytags[name="partner_ids"]').length, 1,
            "partner_ids m2m field added to filter");
        assert.strictEqual(actionManager.controlPanel.$('.o_field_many2manytags[name="partner_categories"]').length, 1,
            "partner_categories m2m field added to filter");
        actionManager.controlPanel.$('.o_search_options a').click();
        // search on partners m2m
        actionManager.controlPanel.$('.o_field_many2one[name="partner_ids"] input').click();
        $('.ui-autocomplete .ui-menu-item a:contains(Genda Swami)').click();
        // search on partner categories m2m
        actionManager.controlPanel.$('.o_field_many2one[name="partner_categories"] input').click();
        $('.ui-autocomplete .ui-menu-item a:contains(Brigadier suryadev singh)').click();
        actionManager.destroy();
    });
});

});
