odoo.define('l10n_cr_d151_account', function (require) {
"use strict";
var core = require('web.core');
var abstractReconciliation = require('account.reconciliation').abstractReconciliation;
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
        })
    }
});

});
