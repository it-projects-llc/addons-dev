/* Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_partner_terms_checkbox.pos', function (require) {

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');

    models.load_fields('res.partner', ['terms_and_conditions']);

    screens.ClientListScreenWidget.include({
        display_client_details: function(visibility, partner, clickpos){
            this._super(visibility, partner, clickpos);
            var self = this;
            var support = this.$('.detail-support.terms_and_conditions');
            var field = this.$('.detail.terms_and_conditions');

            if (support[0] && field[0]) {
                var terms = (this.new_client || this.old_client).terms_and_conditions;
                support[0].checked = terms;
                field[0].value = terms;
                support.off().on('change', function(ev){
                    field[0].value = support[0].checked || '';
                });
            }
            console.log(this);

        },
    });

});
