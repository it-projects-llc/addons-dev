odoo.define('pos_product_category_discount.discount_program', function (require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var Model = require('web.Model');
    var Widget = require('web.Widget');
    var PosDiscountWidget = require('pos_discount.pos_discount');
    var PosBaseWidget = require('point_of_sale.BaseWidget');

    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        export_as_JSON: function(){
            var json = OrderlineSuper.prototype.export_as_JSON.call(this);
            json.discount_program_name = this.discount_program_name || false;
            return json;
        },
        init_from_JSON: function(json) {
            OrderlineSuper.prototype.init_from_JSON.apply(this,arguments);
            this.discount_program_name = json.discount_program_name || false;
        },
        get_discount_name: function(){
            return this.discount_program_name;
        },
    });

    screens.OrderWidget.include({
        set_value: function(val) {
            var self = this;
            var order = this.pos.get_order();
            if (order.get_selected_orderline()) {
                var mode = this.numpad_state.get('mode');
                if( mode === 'discount') {
                    order.get_selected_orderline().discount_program_name = false;
                }
            }
            this._super(val);
        }
    });

    PosBaseWidget.include({
        init:function(parent,options){
            var self = this;
            this._super(parent,options);
            if (this.gui && this.gui.screen_instances.products) {
                var disc_widget = this.gui.screen_instances.products.action_buttons['discount'];
                disc_widget.apply_discount = function(pc) {
                    var order    = self.pos.get_order();
                    var lines    = order.get_orderlines();
                    var product  = self.pos.db.get_product_by_id(self.pos.config.discount_product_id[0]);
                    console.log(self);
                    if (pc !== null) {
                        lines.forEach(function (item){
                            if (item.get_product() === product) {
                                order.remove_orderline(item);
                            }
                        });

                        // Add discount
                        var discount = - pc / 100.0 * order.get_total_with_tax();

                        if( discount < 0 ){
                            order.add_product(product, { price: discount });
                        }
                    }
                };
                disc_widget.button_click = function () {
                    self.gui.show_popup('number', {
                        'title': 'Discount Percentage',
                        'value': self.pos.config.discount_pc,
                        'disc_program': self.pos.discount_program,
                        'confirm': function (val) {
                            if (val) {
                                val = Math.round(Math.max(0, Math.min(100, val)));
                            } else val = null;
                            self.gui.screen_instances.products.action_buttons['discount'].apply_discount(val);
                        },
                    });
                };
            }
            if (this.gui && this.gui.popup_instances['number']) {
                var num_widget = this.gui.popup_instances['number'];
                this.gui.popup_instances['number'].click_confirm = function () {
                    self.gui.close_popup();
                    if( num_widget.options.confirm ){
                        if (num_widget.input_disc_program) {
                            num_widget.get_discount_category(num_widget.discount_program_id);
                        }
                        num_widget.options.confirm.call(num_widget,num_widget.inputbuffer);
                    }
                };
                this.gui.popup_instances['number'].click_numpad = function(event){
                    var newbuf = self.gui.numpad_input(
                        num_widget.inputbuffer,
                        $(event.target).data('action'),
                        {'firstinput': num_widget.firstinput});

                    num_widget.firstinput = (newbuf.length === 0);

                    if (newbuf !== num_widget.inputbuffer) {
                        num_widget.inputbuffer = newbuf;
                        num_widget.$('.value').text(this.inputbuffer);
                    }
                    num_widget.input_disc_program = false;
                }
            }
        },
    });

    models.load_models({
        model: 'pos.discount_program',
        fields: ['discount_program_name','id'],
        loaded: function(self,discount_program){
            if (discount_program) {
                self.discount_program = discount_program;
            }
        },
    });

    PopupWidget.include({
        show: function (options) {
            var self = this;
            this._super(options);
            this.popup_discount = false;
            if (options.disc_program) {
                self.popup_discount = true;
                self.events["click .discount-program-list .button"] = "click_discount_program";
            }
        },
        renderElement: function(){
            this._super();
            if (this.popup_discount) {
                this.$('.popup.popup-number').addClass("popup-discount");
            }
        },
        click_discount_program: function(e) {
            var self = this;
            if (e.currentTarget.id == 'other') {
                console.log("click other button");
            } else {
                this.discount_program_name = e.currentTarget.innerText;
                this.$('.value').text(this.discount_program_name);
                this.input_disc_program = true;
                this.inputbuffer = '';
                this.discount_program_id = Number(e.currentTarget.id);
            }
        },
        get_discount_category: function(id) {
            var self = this;
            var model = new Model('pos.category_discount');
            var domain = [['discount_program_id', '=', id]];
            model.call('search_read', [domain]).then(function (resultat) {
                resultat.forEach(function(item){
                    self.apply_discount_category(item.category_discount_pc, item.discount_category_id[0])
                });
            });
        },
        apply_discount_category: function(discount, category_id) {
            var self = this;
            var order = this.pos.get_order();
            var lines = order.get_orderlines().filter(function (item) { return item.product.pos_categ_id[0] == category_id; });
            lines.forEach(function (item){
                item.discount = discount;
                item.discountStr = discount;
                item.discount_program_name = self.discount_program_name;
                order.get_orderline(item.id).set_discount(discount);
            });
        },
    });
});
