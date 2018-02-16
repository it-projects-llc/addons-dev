odoo.define('pos_multi_session_kitchen.floors', function(require){

    var floors = require('pos_restaurant.floors');
    var chrome = require('pos_multi_session_kitchen.chrome');
    var core = require('web.core');

    var _t = core._t;

    floors.TableWidget.include({
        click_handler: function(){
            var floorplan = this.getParent();
            if (this.pos.config.screen === 'kitchen' && !floorplan.editing && this.pos.config.show_floors_plan) {
                this.pos.table = this.table;
                this.chrome.$el.addClass('kitchen');
                this.gui.show_screen('kitchen');
            } else {
                this._super();
            }
        }
    });

    return floors;
});
