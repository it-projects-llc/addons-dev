odoo.define('pos_multi_session_kitchen.chrome', function (require) {
    "use strict";

    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');

    // Add the FloorScreen to the GUI, and set it as the default screen
    chrome.Chrome.include({
        init: function() {
            this._super();
            var self = this;
            this.pos.ready.done(function(){
                if (self.pos.config.screen === 'kitchen') {
                    self.set_clock(self.$el);
                }
            });
        },
        set_clock: function($el) {
            var self = this;
            var clock = $el.find('.clock');
            if (clock.length) {
                this.updateTime(clock);
                setInterval(function(){
                    self.updateTime(clock);
                }, 1000);
            }
        },
        updateTime: function(clock) {
            function zeroPadding(num, digit) {
                var zero = '';
                for(var i = 0; i < digit; i++) {
                    zero += '0';
                }
                return (zero + num).slice(-digit);
            }
            var cd = new Date();
            var week = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
            var time = zeroPadding(cd.getHours(), 2) + ':' + zeroPadding(cd.getMinutes(), 2) + ':' + zeroPadding(cd.getSeconds(), 2);
            var date = zeroPadding(cd.getFullYear(), 4) + '-' + zeroPadding(cd.getMonth()+1, 2) + '-' + zeroPadding(cd.getDate(), 2) + ' ' + week[cd.getDay()];
            this.update_clock(clock, time, date);
        },
        update_clock: function(clock, time, date) {
            clock.find('.date').html(date);
            clock.find('.time').html(time);
        },
        build_widgets: function(){
            this._super();
            if (this.pos.config.screen === 'kitchen' && !this.pos.config.show_floors_plan) {
                this.$el.addClass('kitchen');
                this.gui.set_startup_screen('kitchen');
            }
        }
    });

//    chrome.OrderSelectorWidget.include({
//        init: function(parent, options) {
//            this._super(parent, options);
//        }
//    });
});
