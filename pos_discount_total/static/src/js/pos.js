odoo.define('pos_discount_total.OrderWidget', function(require) {
    "use strict";

    var screens = require('point_of_sale.screens');

    screens.OrderWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent,options);
            this.summary_selected = false;

            var line_click_handler = this.line_click_handler;
            this.line_click_handler = function(event){
                self.deselect_summary();
                line_click_handler.call(this, event)
            };
        },
        select_summary:function(){
            if (this.summary_selected)
                return;
            this.deselect_summary();
            this.summary_selected = true;
            $('.order .summary').addClass('selected');
            this.numpad_state.reset();
            this.numpad_state.changeMode('discount');
        },
        deselect_summary:function(){
            this.summary_selected = false;
            $('.order .summary').removeClass('selected')
        },
        set_value: function(val){
            if (!this.summary_selected)
                return this._super(val);
            var mode = this.numpad_state.get('mode');
            if (mode=='discount'){
                var order = this.pos.get_order();
                $.each(order.orderlines.models, function (k, line){
                    line.set_discount(val)
                })
            }
        },
        renderElement:function(scrollbottom){
            var self = this;
            this._super(scrollbottom);
            $(this.el).click(function(event){
                if (event.target.classList.contains('summary')){
                    self.pos.get_order().deselect_orderline(this.orderline);
                    self.numpad_state.reset();
                    self.select_summary();
                }
            });
        }
    });

});
