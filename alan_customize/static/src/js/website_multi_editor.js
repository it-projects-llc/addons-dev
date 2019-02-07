odoo.define('alan_customize.website_multi_editor', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var weContext = require('web_editor.context');
    var web_editor = require('web_editor.editor');
    var options = require('web_editor.snippets.options');
    var wUtils = require('website.utils');
    var _t = core._t;

    var multi_tab_configure = options.Class.extend({
        popup_template_id: "editor_new_multi_tab_configure_template",
        popup_title: _t("Select Collection"),
        select_collection: function (type, value) {
            var self = this;
            var def = wUtils.prompt({
                'id': this.popup_template_id,
                'window_title': this.popup_title,
                'select': _t("Collection"),
                'init': function (field) {
                    return rpc.query({
                        model: 'collection.configure',
                        method: 'name_search',
                        args: ['', []],
                        context: weContext.get(),
                    });
                },
            });
            def.then(function (collection_id) {
                self.$target.attr("data-list-id", collection_id);
                ajax.jsonRpc('/web/dataset/call','call',{
                        model: 'collection.configure',
                        method: 'read',
                        args: [[parseInt(collection_id)],['name'],weContext.get()],
                    }).then(function (data){
                        if(data && data[0] && data[0].name)
                            self.$target.empty().append('<div class="container"><div class="product_slide" contentEditable="false"><div class="col-md-12"><div class="seaction-head"<h1>'+ data[0].name +'</h1></div></div></div></div>');                                  
                    });
                });
            return def;
        },
        onBuilt: function () {
            var self = this;
            this._super();
            this.select_collection('click').fail(function () {
                self.getParent()._onRemoveClick($.Event( "click" ));
            });
        }
    });


    options.registry.s_product_multi_with_header = multi_tab_configure.extend({
        cleanForSave: function () {
            $('.js_multi_collection').empty();
        },
    });

    options.registry.s_product_multi_snippet = multi_tab_configure.extend({
        cleanForSave: function () {
            $('.multi_tab_product_snippet').empty();
        },
    });
});
