odoo.define('l10n_cr_d151_account', function (require) {
"use strict";
var core = require('web.core');
var abstractReconciliation = require('account.reconciliation').abstractReconciliation;
var bankStatementReconciliationLine = require('account.reconciliation').bankStatementReconciliationLine;
var bankStatementReconciliation = require('account.reconciliation').bankStatementReconciliation;
var Model = require('web.DataModel');
var _t = core._t;

var FieldMany2One = core.form_widget_registry.get('many2one');


abstractReconciliation.include({
    init: function (parent, context) {
        this._super(parent);
        _.extend(this.create_form_fields, {
            cr_d151_category_id: {
                id: "cr_d151_category_id",
                index: 25,
                corresponding_property: 'cr_d151_category_id',
                label: _t('D151 category'),
                required: true,
                constructor: FieldMany2One,
                    field_properties: {
                    relation: "account.cr.d151.category",
                    string: _t("D151 category"),
                    type: "many2one",
                },
            }
        });
    },

});

bankStatementReconciliationLine.include({
    initializeCreateForm: function () {
        var self = this;
        this._super();
        this.cr_d151_category_id_field.set('value', this.st_line.cr_d151_category_id);
        this.account_id_field.on('change:value', this, function() {
            new Model('account.bank.statement.line').
            call('reconciliation_widget_on_change_account',
                [this.st_line.id, self.account_id_field.get('value')]).
            then(function(result) {
                if (result) {
                    self.cr_d151_category_id_field.set('value', result);
                }
            });
        });
    },

    prepareDataForPersisting: function () {
        var result = this._super();
        var cr_d151_category_id = this.cr_d151_category_id_field.get('value');
        for (var i=0; i<result['new_aml_dicts'].length; i++) {
            result['new_aml_dicts'][i]['cr_d151_category_id'] = cr_d151_category_id;
        }
        return result;
    },

    persistAndBowOut: function () {
        var cr_d151_category_id = this.cr_d151_category_id_field.get('value');
        if (cr_d151_category_id && this.st_line.has_no_partner) {
            alert('You need to select a partner to use the D151 category.')
            return;
        }
        this._super()
    }
});

});
