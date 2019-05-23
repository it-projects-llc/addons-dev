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

                    var partner = self.pos.get_order().get_client();
                    if (partner) {
                        self.send_mail_receipt(partner.id);
                    } else {
                        self.set_mail_customer = true;
                        self.$el.zIndex(-6);
                        self.pos.gui.screen_instances.clientlist.show();
                    }
                });
            }
        },

        send_mail_receipt: function(partner_id) {
            var receipt  = QWeb.render('PosTicket', this.get_receipt_render_env());
            return rpc.query({
                model: 'pos.config',
                method: 'send_receipt_via_mail',
                args: [partner_id, receipt],
            }, {
                shadow: true,
            }).then(function (res) {
                console.log('THEN AFTER SENDING');
            });
        }
    });

    screens.ClientListScreenWidget.include({
        back: function() {
            if (this.pos.get_order().finalized) {
                // means we came there from the receipt screen
                this.close();
                var receipt_screen = this.pos.gui.screen_instances.receipt;
                receipt_screen.show();
                receipt_screen.$el.zIndex(0);
            } else {
                this._super();
            }
        },

        save_changes: function(){
            var order = this.pos.get_order();
            if( this.has_client_changed() &&
                this.pos.config.send_receipt_by_mail &&
                this.gui.current_screen.set_mail_customer) {

                this.gui.screen_instances.receipt.send_mail_receipt(this.new_client.id);
            } else {
                this._super();
            }
        },
    });

});
