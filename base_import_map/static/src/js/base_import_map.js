odoo.define('base_import_map.map', function (require) {
    "use strict";

    var ControlPanelMixin = require('web.ControlPanelMixin');
    var BaseImport = require('base_import.import');
    var core = require('web.core');
    var Model = require('web.Model');

    var QWeb = core.qweb;
    var _lt = core._lt;
    var _t = core._t;

    BaseImport.DataImport.include({
        init: function (parent, action) {
            var self = this;
            this._super(parent, action);
            this.settings_checked = false;
            this.opts.push({name: 'settings', label: _lt("Settings:"), value: '666'});
            this.events['click .oe_import_set_settings'] = function (e) {
                self.display_setting_name(e);
            };
        },
        start: function() {
            var self = this;
            this.setup_settings_picker();
            this._super();
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
        setup_settings_picker: function(){
            var self = this;
            var model = new Model("base_import_map.map");
            model.call('name_search', [[]]).then(function(res){
                var suggestions = [];
                if (res) {
                    res.forEach(function (item) {
                        suggestions.push({id: item.id, text: _t(item.name)})
                    })
                } else {
                    suggestions.push({id: "None", text: _t("None")})
                }
                self.$('input.oe_import_settings').select2({
                    width: '160px',
                    query: function (q) {
                        if (q.term) {
                            suggestions.unshift({id: q.term, text: q.term});
                        }
                        q.callback({results: suggestions});
                    },
                    initSelection: function (e, c) {
                        return c({id: "None", text: _t("None")});
                    },
                });
            });
        },
        render_buttons: function(){
            this._super();
            var self = this;
            this.$buttons.filter('.o_import_import').on('click', function(){
                self.import.bind(this);
                self.do_save_settings();
            });
        },
        do_save_settings: function() {
            var self = this;
            this.setting_name = $(".oe_import_settings_name").val();
            // if (this.settings_checked && this.setting_name) {
            //     var model = new Model("base_import_map.map");
            //     var value = {
            //         name: self.setting_name,
            //         external_id_generator: self.external_id_generator,
            //         model_id: self.model_id,
            //         line_ids: self.line_ids,
            //     };
            //     model.call('create', [[]]).then(function(res){
            //     //    save value
            //     })
            // }
        },
    });
});
