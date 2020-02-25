odoo.define('garazd_loyalty.screens', function(require){
    "use strict";

    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var _t = core._t;


    screens.ScreenWidget.include({

        barcode_client_action: function(code){

            var self = this;
            var partner = this.pos.db.get_partner_by_barcode(code.code);
            var order = this.pos.get_order();

            if(partner){
                return this._super(code);
            }

            var show_code = code.code;
            var new_partner_id = null;

            this.gui.show_popup('confirm',{
                'title': _t('New Discount Card scanned.'),
                'body': _t('Issue a card to the client?'),
                confirm: function() {
                    var client_list_screen = self.gui.screen_instances.clientlist;
                    var fields = {};
                    fields.country_id   = self.pos.company.country_id[0] || false;
                    fields.name         = show_code || false;
                    fields.barcode      = show_code || false;


                    rpc.query({
                            model: 'res.partner',
                            method: 'create_from_ui',
                            args: [fields],
                        })
                        .then(function(partner_id){

                            self.pos.load_new_partners().then(function(){
                                var new_partner = self.pos.db.get_partner_by_id(partner_id);
                                order.set_client(new_partner);
                                order.card_offered = true;
                            });

                        },function(err,ev){
                            ev.preventDefault();
                            var error_body = _t('Your Internet connection is probably down.');
                            if (err.data) {
                                var except = err.data;
                                error_body = except.arguments && except.arguments[0] || except.message || error_body;
                            }
                            self.gui.show_popup('error',{
                                'title': _t('Error: Could not Save Changes'),
                                'body': error_body,
                            });
                            contents.on('click','.button.save',function(){ self.save_client_details(partner); });
                        });

                    client_list_screen.reload_partners()







                },

            });

            return false;
        }

    });



    screens.OrderWidget.include({
        set_value: function(val) {
            var mode = this.numpad_state.get('mode');
            if(mode != 'discount') {
                this._super(val);
            }
        }

    });

    return screens;

});
