odoo.define('base_import_map.map', function (require) {
    "use strict";

    var ControlPanelMixin = require('web.ControlPanelMixin');
    var BaseImport = require('base_import.import');
    var core = require('web.core');
    var Model = require('web.Model');

    var _lt = core._lt;

    BaseImport.DataImport.include({
        init: function (parent, action) {
            var self = this;
            this._super(parent, action);
            this.settings_checked = false;
            this.opts.push({name: 'settings', label: _lt("Settings:"), value: ''});
            this.events['click .oe_import_set_settings'] = function (e) {
                self.display_setting_name(e);
            };
        },
        onfile_loaded: function () {
            this.load_settings();
            this._super()
        },
        display_setting_name: function(e){
            var self = this;
            if (this.settings_checked) {
                $("input[class='oe_import_settings_name']").hide();
                self.settings_checked = false;
            } else {
                $("input[class='oe_import_settings_name']").show();
                self.settings_checked = true;
            }
        },
        load_settings: function() {
            var self = this;
            var model = new Model("base_import_map.map");
            model.call('search_read', [[]]).then(function(res){
                self.show_settings_list(res);
            });
        },
        show_settings_list: function(list){

        },
    });
});
