/* Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_inventory_adjustment.ui', function (require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var gui = require('point_of_sale.gui');
    var Model = require('web.DataModel');
    var core = require('web.core');
    var _t = core._t;


    var NewStageButton = screens.ActionButtonWidget.extend({
        template: 'NewStageButton',
        button_click: function () {
            var self = this;
            this.gui.show_popup('invadjnew',{
                'title': _t('New Stage'),
                'confirm': function(data){
                    return new Model('stock.inventory.stage').call('create', [data]).then(function (res) {
                        return self.pos.get_inventory_stages([res]).then(function(stage){
                            create_inventory_order(stage, {});
                        });
                    }, function (err) {
                        console.log(err);
                    });
                },
                'cancel':  function(){
                    this.gui.close_popup();
                }
            });
        },
    });
    screens.define_action_button({
        'name': 'new_stage_button',
        'widget': NewStageButton,
        'condition': function () {
            return this.pos.config.inventory_adjustment;
        },
    });


    var UpdateStageButton = screens.ActionButtonWidget.extend({
        template: 'UpdateStageButton',
        button_click: function () {
            var pos = this.pos;
            pos.get_inventory_stages().then(function(list){
                pos.gui.show_popup('invadj',{
                    'title': _t('Select Inventory Stage'),
                    'list': list,
                    'confirm': function(inv){
                        var lines = pos.get_inventory_stage_lines(inv.line_ids).then(function(lines){
                            pos.create_inventory_order(inv, {
                                inv_adj_lines: lines,
                            });
                        });
                    },
                    'cancel':  function(){
                        pos.gui.close_popup();
                    }
                });
            })
        },
    });
    screens.define_action_button({
        'name': 'update_stage_button',
        'widget': UpdateStageButton,
        'condition': function () {
            return this.pos.config.inventory_adjustment;
        },
    });


    var InventorySelectionPopupWidget = PopupWidget.extend({
        template: 'InventorySelectionPopupWidget',
        show: function(options){
            options = options || {};
            var self = this;
            this._super(options);

            this.list = options.list || [];
            this.renderElement();
        },
        click_item : function(event) {
            this.gui.close_popup();
            if (this.options.confirm) {
                var item = this.list[parseInt($(event.target).data('item-index'))];
                this.options.confirm.call(self,item);
            }
        }
    });
    gui.define_popup({name:'invadj', widget: InventorySelectionPopupWidget});


    var NewInventoryPopupWidget = PopupWidget.extend({
        template: 'NewInventoryPopupWidget',
        show: function(options){
            options = options || {};
            var self = this;
            this._super(options);

            this.list = options.list || [];
            this.renderElement();
        },
        click_confirm : function(event) {
            var data = {
                inventory_id: parseInt(this.$el.find('select.inventory').val()),
                user_id: parseInt(this.$el.find('select.user').val()),
                name: this.$el.find('input.name').val(),
                note: this.$el.find('input.note').val(),
            }
            this.gui.close_popup();
            if (this.options.confirm) {
                this.options.confirm.call(self,data);
            }
        },
    });
    gui.define_popup({name:'invadjnew', widget: NewInventoryPopupWidget});


    screens.ActionpadWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);

             this.pos.bind('change:referrer', function() {
                self.renderElement();
            });
        },

        renderElement: function() {
            this._super();
            if (this.pos.config.inventory_adjustment) {
                this.update_ui_for_inventory_adjustment();
            }
        },

        update_ui_for_inventory_adjustment: function() {
            var self = this;
            this.$('.button.set-customer').off().hide();
            this.$('.button.pay').off().click(function(){
                self.gui.show_popup('confirm',{
                    'title': _t('Inventory Validation'),
                    'body':  _t('Are you sure you want to Validate current inventory stage?'),
                    confirm: function(){
                        console.log('asdsadsadsadsadsadasd')
                    },
                });
            });
//            this.$('.numpad button[data-mode="discount"]').text('').off().addClass('disable');
//            this.$('.numpad button[data-mode="price"]').text('').off().addClass('disable');
//            this.$('.numpad button.numpad-minus').text('').off().addClass('disable');
        },
    });

    return {
        NewStageButton: NewStageButton,
        UpdateStageButton: UpdateStageButton,
        NewInventoryPopupWidget: NewInventoryPopupWidget,
        InventorySelectionPopupWidget: InventorySelectionPopupWidget,
    }
});
