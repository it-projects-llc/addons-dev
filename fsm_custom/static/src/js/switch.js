odoo.define('fsm_custom.switch', function (require) {
"use strict";

var common = require('web.form_common');
var core = require('web.core');
var crash_manager = require('web.crash_manager');
var data = require('web.data');
var Dialog = require('web.Dialog');
var FormRenderingEngine = require('web.FormRenderingEngine');
var Model = require('web.DataModel');
var Pager = require('web.Pager');
var Sidebar = require('web.Sidebar');
var utils = require('web.utils');
var View = require('web.View');
var FormView = require('web.FormView');

var _t = core._t;

//var SalesTeamDashboardView = require('sales_team.dashboard');


FormView.include({
//    do_show: function (options) {
//        var self = this;
//        options = options || {};
//        this.$el.removeClass('oe_form_dirty');
//
//        var shown = this.has_been_loaded;
//        if (options.reload !== false) {
//            shown = shown.then(function() {
//                if (self.dataset.index === null) {
//                    // null index means we should start a new record
//                    return self.on_button_new();
//                }
//                var fields = _.keys(self.fields_view.fields);
//                fields.push('display_name');
//                fields.push('__last_update');
//                return self.dataset.read_index(fields, {
//                    context: { 'bin_size': true }
//                }).then(function(r) {
//                    self.trigger('load_record', r);
//                });
//            });
//        }
//        return $.when(shown, this._super()).then(function() {
//            self._actualize_mode(options.mode || self.options.initial_mode);
//            core.bus.trigger('form_view_shown', self);
//        });
//    },


    _get_onchange_values: function() {
        var field_values = this.get_fields_values();
        console.log(">>>>>>field_values",field_values)
        console.log(">>>>>>field_values",this)
        if (field_values.id.toString().match(data.BufferedDataSet.virtual_id_regex)) {
            delete field_values.id;
        }
        if (this.dataset.parent_view) {
            // this belongs to a parent view: add parent field if possible
            var parent_view = this.dataset.parent_view;
            var child_name = this.dataset.child_name;
            var parent_name = parent_view.get_field_desc(child_name).relation_field;
            if (parent_name) {
                // consider all fields except the inverse of the parent field
                var parent_values = parent_view.get_fields_values();
                delete parent_values[child_name];
                field_values[parent_name] = parent_values;
            }
        }
        return field_values;
    },

    do_onchange: function(widget) {
        var self = this;
        console.log(">>>>>>self",self)
        if (self.fields.custom_install_color){
            if (self.fields.custom_install_color.$checkbox[0].checked){
                if ($('.o_check_value')){
                    $('.o_check_value >a ').css({"background-color": "#0DF74B"});

                 }

                }
            else
                if ($('.o_check_value')){
                    $('.o_check_value >a ').css({"background-color": "##D3DCDC"});
                 }
         }
         if (self.fields.custom_damage_color){
            if (self.fields.custom_damage_color.$checkbox[0].checked){
                if ($('.o_check_value_damage')){
                    $('.o_check_value_damage >a ').css({"background-color": "#0DF74B"});

                 }

                }
            else
                if ($('.o_check_value_damage')){
                    $('.o_check_value_damage >a ').css({"background-color": "##D3DCDC"});
                 }
         }


            


        if (self._onchange_specs === undefined) {
            self._build_onchange_specs();
        }
        var onchange_specs = self._onchange_specs;
        try {
            var def = $.when({});
            var change_spec = widget ? onchange_specs[widget.name] : null;
            if (!widget || (!_.isEmpty(change_spec) && change_spec !== "0")) {
                var ids = [],
                    trigger_field_name = widget ? widget.name : self._onchange_fields,
                    values = self._get_onchange_values(),
                    context = new data.CompoundContext(self.dataset.get_context());

                if (widget && widget.build_context()) {
                    context.add(widget.build_context());
                }
                if (self.dataset.parent_view) {
                    var parent_name = self.dataset.parent_view.get_field_desc(self.dataset.child_name).relation_field;
                    context.add({field_parent: parent_name});
                }

                if (self.datarecord.id && !data.BufferedDataSet.virtual_id_regex.test(self.datarecord.id)) {
                    // In case of a o2m virtual id, we should pass an empty ids list
                    ids.push(self.datarecord.id);
                }
                def = self.alive(self.dataset.call(
                    "onchange", [ids, values, trigger_field_name, onchange_specs, context]));
            }
            this.onchanges_mutex.exec(function(){
                return def.then(function(response) {
                    var fields = {};
                    if (widget){
                        fields[widget.name] = widget.field;
                    }
                    else{
                        fields = self.fields_view.fields;
                    }
                    var defs = [];
                    _.each(fields, function(field, fieldname){
                        if (field && field.change_default) {
                            var value_;
                            if (response.value && (fieldname in response.value)) {
                                // Use value from onchange if onchange executed
                                value_ = response.value[fieldname];
                            } else {
                                // otherwise get form value for field
                                value_ = self.fields[fieldname].get_value();
                            }
                            var condition = fieldname + '=' + value_;

                            if (value_) {
                                defs.push(self.alive(new Model('ir.values').call(
                                    'get_defaults', [self.model, condition]
                                )).then(function (results) {
                                    if (!results.length) {
                                        return response;
                                    }
                                    if (!response.value) {
                                        response.value = {};
                                    }
                                    for(var i=0; i<results.length; ++i) {
                                        // [whatever, key, value]
                                        var triplet = results[i];
                                        response.value[triplet[1]] = triplet[2];
                                    }
                                    return response;
                                }));
                            }
                        }
                    });
                    return _.isEmpty(defs) ? response : $.when.apply(null, defs);
                }).then(function(response) {
                    return self.on_processed_onchange(response);
                });
            });
            return this.onchanges_mutex.def;
        } catch(e) {
            console.error(e);
            crash_manager.show_message(e);
            return $.Deferred().reject();
        }
    },
    on_processed_onchange: function(result) {
        try {
        var fields = this.fields;
        _(result.domain).each(function (domain, fieldname) {
            var field = fields[fieldname];
            if (!field) { return; }
            field.node.attrs.domain = domain;
        });

        var def = $.when(!_.isEmpty(result.value) && this._internal_set_values(result.value));

        // FIXME XXX a list of warnings?
        if (!_.isEmpty(result.warning)) {
            this.warning_displayed = true;
            var dialog = new Dialog(this, {
                size: 'medium',
                title:result.warning.title,
                $content: QWeb.render("CrashManager.warning", result.warning)
            });
            dialog.open();
            dialog.on('closed', this, function () {
                this.warning_displayed = false;
            });
        }

        return def;
        } catch(e) {
            console.error(e);
            crash_manager.show_message(e);
            return $.Deferred().reject();
        }
    },

//    do_show: function (options) {
//        var self = this;
//        options = options || {};
//        this.$el.removeClass('oe_form_dirty');
//
//        var shown = this.has_been_loaded;
//        if (options.reload !== false) {
//            shown = shown.then(function() {
//                if (self.dataset.index === null) {
//                    // null index means we should start a new record
//                    return self.on_button_new();
//                }
//                var fields = _.keys(self.fields_view.fields);
//                fields.push('display_name');
//                fields.push('__last_update');
//                return self.dataset.read_index(fields, {
//                    context: { 'bin_size': true }
//                }).then(function(r) {
//                    self.trigger('load_record', r);
//                });
//            });
//        }
//        return $.when(shown, this._super()).then(function() {
//            self._actualize_mode(options.mode || self.options.initial_mode);
//            core.bus.trigger('form_view_shown', self);
////            if (self.fields.custom_install_color){
////                if (self.fields.custom_install_color.$checkbox[0].checked){
////                    if ($('.o_check_value')){
////                        $('.o_check_value >a ').css({"background-color": "#0DF74B"});
////
////                     }
////
////                    }
////                else
////                    if ($('.o_check_value')){
////                        $('.o_check_value >a ').css({"background-color": "##D3DCDC"});
////                     }
////                }
////            if (self.fields.custom_damage_color){
////                    if (self.fields.custom_damage_color.$checkbox[0].checked){
////                        if ($('.o_check_value_damage')){
////                            $('.o_check_value_damage >a ').css({"background-color": "#0DF74B"});
////
////                         }
////
////                        }
////                    else
////                        if ($('.o_check_value_damage')){
////                            $('.o_check_value_damage >a ').css({"background-color": "##D3DCDC"});
////                         }
////                 }
//
//        });
//    },
    load_record: function(record) {
        var self = this, set_values = [];
        if (!record) {
            this.set({ 'title' : undefined });
            this.do_warn(_t("Form"), _t("The record could not be found in the database."), true);
            return $.Deferred().reject();
        }
        this.datarecord = record;
        if (record.custom_install_color){
            console.log("change",record.custom_install_color)
            if ($('.o_check_value')){
                    $('.o_check_value >a ').css({"background-color": "#0DF74B"});

                 }

                }
        else
            if ($('.o_check_value')){
                $('.o_check_value >a ').css({"background-color": "##D3DCDC"});
             }

        if (record.custom_damage_color){
            console.log("change",record.custom_damage_color)
            if ($('.o_check_value_damage')){
                    $('.o_check_value_damage >a ').css({"background-color": "#0DF74B"});

                 }

                }
        else
            if ($('.o_check_value_damage')){
                $('.o_check_value_damage >a ').css({"background-color": "##D3DCDC"});
             }


        this.record_loaded = $.Deferred();
        _(this.fields).each(function (field, f) {
            field._dirty_flag = false;
            field._inhibit_on_change_flag = true;
            var result = field.set_value_from_record(self.datarecord);
            field._inhibit_on_change_flag = false;
            set_values.push(result);
        });
        this._actualize_mode(); // call after updating the fields as it may trigger a re-rendering
        this.set({ 'title' : record.id ? record.display_name : _t("New") });
        this.update_pager(); // the mode must be actualized before updating the pager
        return $.when.apply(null, set_values).then(function() {
            if (!record.id) {
                // trigger onchange for new record after x2many with non-embedded views are loaded
                var fields_loaded = _.pluck(self.fields, 'is_loaded');
                $.when.apply(null, fields_loaded).done(function() {
                    self.do_onchange(null);
                });
            }
            self.on_form_changed();
            self.rendering_engine.init_fields().then(function() {
                self.is_initialized.resolve();
                self.record_loaded.resolve();
                if (self.sidebar) {
                    self.sidebar.do_attachement_update(self.dataset, self.datarecord.id);
                }
                if (record.id) {
                    self.do_push_state({id:record.id});
                     if (record.custom_install_color){
                        console.log("change",record.custom_install_color)
                        if ($('.o_check_value')){
                                $('.o_check_value >a ').css({"background-color": "#0DF74B"});

                             }

                            }
                     else
                        if ($('.o_check_value')){
                            $('.o_check_value >a ').css({"background-color": "##D3DCDC"});
                         }

                     if (record.custom_damage_color){
                        console.log("change",record.custom_damage_color)
                        if ($('.o_check_value_damage')){
                                $('.o_check_value_damage >a ').css({"background-color": "#0DF74B"});

                             }

                            }
                     else
                        if ($('.o_check_value_damage')){
                            $('.o_check_value_damage >a ').css({"background-color": "##D3DCDC"});
                         }
                } else {
                    self.do_push_state({});
                }
                self.$el.removeClass('oe_form_dirty');
            });
         });
    },
    });

//basicmodel.include({
//    _applyChange: function (recordID, changes, options) {
//            var self = this;
//            var record = this.localData[recordID];
//            var field;
//            var defs = [];
//            options = options || {};
//            record._changes = record._changes || {};
//            if (!options.doNotSetDirty) {
//                record._isDirty = true;
//            }
//            console.log(">>>self>",self)
//            dshdjhshdlsfjkjfsjfks
//            dialog.alert()
////            if (self.__parentedParent.modelName == "project.task") {
////                 if (changes.company_id) {
////
////                     var companyID = changes.company_id.id;
////                        this._rpc({
////                            model: 'res.users',
////                            method: 'write',
////                            args: [[session.uid], {'company_id': companyID}],
////                        })
////                        .then(function() {
////                            location.reload();
////                        });
////
////                 }
////
////
////            }
//
//            var initialData = {};
//            this._visitChildren(record, function (elem) {
//                initialData[elem.id] = $.extend(true, {}, _.pick(elem, 'data', '_changes'));
//            });
//            console.log('context.................',changes)
//            // apply changes to local data
//            for (var fieldName in changes) {
//                field = record.fields[fieldName];
//
//                if (field.type === 'one2many' || field.type === 'many2many') {
//                    defs.push(this._applyX2ManyChange(record, fieldName, changes[fieldName], options.viewType, options.allowWarning));
//                } else if (field.type === 'many2one' || field.type === 'reference') {
//                    defs.push(this._applyX2OneChange(record, fieldName, changes[fieldName]));
//                } else {
//                    record._changes[fieldName] = changes[fieldName];
//                }
//            }
//
//            if (options.notifyChange === false) {
//                return $.Deferred().resolve(_.keys(changes));
//            }
//
//
//            return $.when.apply($, defs).then(function () {
//                var onChangeFields = []; // the fields that have changed and that have an on_change
//                for (var fieldName in changes) {
//                    field = record.fields[fieldName];
//                    if (field.onChange) {
//                        var isX2Many = field.type === 'one2many' || field.type === 'many2many';
//                        if (!isX2Many || (self._isX2ManyValid(record._changes[fieldName] || record.data[fieldName]))) {
//                            onChangeFields.push(fieldName);
//                        }
//                    }
//                }
//                var onchangeDef = $.Deferred();
//                if (onChangeFields.length) {
//                    self._performOnChange(record, onChangeFields, options.viewType)
//                        .then(function (result) {
//                            delete record._warning;
//                            onchangeDef.resolve(_.keys(changes).concat(Object.keys(result && result.value || {})));
//                        }).fail(function () {
//                            self._visitChildren(record, function (elem) {
//                                _.extend(elem, initialData[elem.id]);
//                            });
//                            onchangeDef.resolve({});
//                        });
//                } else {
//                    onchangeDef = $.Deferred().resolve(_.keys(changes));
//                }
//                return onchangeDef.then(function (fieldNames) {
//                    _.each(fieldNames, function (name) {
//                        if (record._changes && record._changes[name] === record.data[name]) {
//                            delete record._changes[name];
//                            record._isDirty = !_.isEmpty(record._changes);
//                        }
//                    });
//                    return self._fetchSpecialData(record).then(function (fieldNames2) {
//                        // Return the names of the fields that changed (onchange or
//                        // associated special data change)
//                        return _.union(fieldNames, fieldNames2);
//                    });
//                });
//            });
//        },
//    });
})