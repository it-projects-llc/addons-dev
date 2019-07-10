odoo.define('potential_candidate.ht_get_digital_approval',function(require){
    "use strict";

    var core = require('web.core');
    var data = require('web.data');
    var BasicFields= require('web.basic_fields');
    var FormView = require('web.FormView');
    var Registry = require('web.field_registry');
    var utils = require('web.utils');
    var session = require('web.session');
    var _t = core._t;
    var QWeb = core.qweb;
    var images = {};

    var DigitalSignature = BasicFields.FieldBinaryImage.extend({
        template: 'DigitalSignature',
        _render: function() {
            var self=this;
            this._super();
            this.$el.find('> img').remove();
            var canvas = this.$el.find("canvas");
            var c_height = canvas[0].height
            var c_width = canvas[0].width
            canvas = canvas[0];
            var ratio =  Math.max(window.devicePixelRatio || 1, 1);
            canvas.width = c_width * ratio;
            canvas.height = c_height * ratio;

            this.signaturePad = new SignaturePad(canvas);
            this.$el.find("[data-action=clear]").click(function(){
                console.log("in clear",this);
                self.signaturePad.clear();
            });
            this.$el.find("[data-action=save]").on('click',function(){
                console.log("DigitalSignature",DigitalSignature);
                console.log("in save 2",this);
                var val = self.signaturePad.toDataURL();
                var new_val = val.split(",")[1];
                self['value'] = new_val;
                self._on_save_sign(this);
            });
        },
        _on_save_sign: function(prepend_on_create) {
            var self = this;
            this.$('> img').remove();
            var signature = this.$(".signature").jSignature("getData", 'image');
            var is_empty = signature ?
                self.empty_sign[1] === signature[1] :
                false;
            if (!is_empty && typeof signature !== "undefined" && signature[1]) {
                this._setValue(signature[1]);
            }
        },
    });

    Registry.add('digi-signature', DigitalSignature);

    FormView.include({
        save: function(prepend_on_create) {
            this.save_list = [];
            var self = this;
            if(this.model === "digital.sign.popup"){
                console.log($(".save_sign"));
                $(".save_sign").click();
            }
            var save_obj = {prepend_on_create: prepend_on_create, ret: null};
            console.log("in save",this);
            this.save_list.push(save_obj);
            return self._process_operations().then(function() {
                if (save_obj.error)
                    return $.Deferred().reject();
                return $.when.apply($, save_obj.ret);
            }).done(function(result) {
                self.$el.removeClass('oe_form_dirty');
            });
        },
    });
});