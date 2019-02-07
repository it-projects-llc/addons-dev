odoo.define('alan_customize.editor_blog', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var weContext = require('web_editor.context');
    var web_editor = require('web_editor.editor');
    var options = require('web_editor.snippets.options');
    var wUtils = require('website.utils');
    var _t = core._t;

    var blog_common = options.Class.extend({
        popup_template_id: "editor_new_blog_slider_template",
        popup_title: _t("Select Collection"),
        website_blog_configure: function (previewMode, value) {
            var self = this;
            var def = wUtils.prompt({
                'id': this.popup_template_id,
                'window_title': this.popup_title,
                'select': _t("Collection"),
                'init': function (field) {
                    return rpc.query({
                        model: 'blog.configure',
                        method: 'name_search',
                        args: ['', []],
                        context: weContext.get(),
                    });
                },
            });
            def.then(function (collection_id) {
                self.$target.attr("data-blog_list-id", collection_id);
                rpc.query({
                    model :'blog.configure',
                    method:'read',
                    args: [[parseInt(collection_id)]],
                    context: weContext.get()
                }).then(function (data){
                    if(data && data[0] && data[0].name)
                    {
                     self.$target.empty().append('<div class="seaction-head"><h1>'+ data[0].name+'</h1></div>');   
                    }
                });
            });
            return def;
        },
        onBuilt: function () {
            var self = this;
            this._super();
            this.website_blog_configure('click').fail(function () {
                self.getParent()._onRemoveClick($.Event( "click" ));
            });
        }
    });
    options.registry.latest_blog = blog_common.extend({
        cleanForSave: function(){
            this.$target.addClass("hidden");
        }
    });
});
