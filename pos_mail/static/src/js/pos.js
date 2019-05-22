/* Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_mail.pos', function (require) {

    var screens = require('point_of_sale.screens');
//    var models = require('point_of_sale.models');
//    var gui = require('point_of_sale.gui');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var QWeb = core.qweb;

//    var PosModelSuper = models.PosModel;
//    models.PosModel = models.PosModel.extend({
//        initialize: function(){
//            PosModelSuper.prototype.initialize.apply(this, arguments);
//        },
//
//    });
//
//    gui.Gui.prototype.screen_classes.filter(function(el) {
//        return el.name === 'clientlist';
//    })[0].widget.include({
//
//    });

    screens.ReceiptScreenWidget.include({
        renderElement: function() {
            this._super();
            var self = this;
            if (this.pos.config.send_receipt_by_mail) {
                this.$('.button.mail_receipt').click(function(){
                    var receipt  = self.get_receipt_xml();
                    var partner = self.pos.get_order().get_client();
                    if (partner) {
                        self.send_mail_receipt(partner.id, receipt);
                    } else {
                        console.log('SET PARTNER BASTARD')
                    }
                    console.log('AAAAA', receipt)
                });
            }
        },

        get_receipt_xml: function() {
            return QWeb.render('PosTicket', this.get_receipt_render_env());
        },

        send_mail_receipt: function(partner_id, receipt) {
            return rpc.query({
                model: 'pos.config',
                method: 'send_receipt_via_mail',
                args: [partner_id, receipt],
            }, {
                shadow: true,
            }).then(function (res) {
                console.log('THEN AFTER SENDING')
            });
        }
    })
});
