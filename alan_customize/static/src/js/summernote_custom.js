odoo.define('alan_customize.embeded_snippet',function(require) {
  'use strict';
  var core = require('web.core');
  var QWeb = core.qweb;
  var options = require('web_editor.snippets.options');
  var ajax = require('web.ajax');
  var _t = core._t;
  var Dialog = require('web.Dialog');
  ajax.loadXML('/alan_customize/static/src/xml/summer_note.xml', core.qweb);
  options.registry.summernote_embeded = options.Class.extend({
    xmlDependencies: ['/alan_customize/static/src/xml/summer_note.xml'],
    start : function () {
      var self = this;
      this.id = this.$target.attr("id");
      var markupStr =this.$target.html();
    },
    modify_note : function(type,value) {
      var self = this;
      this.id = this.$target.attr("id");
      var markupStr =this.$target.html();
      if(type == false || type == 'click'){
        var dialog =new Dialog(self, {
          size: 'medium',
          title: 'Alan Snippet Builder',
          buttons: [{text: _t('Save'), classes: 'btn-primary', close: true, click: function () {
            var new_qty = $('#summernote_text').val();
            var data = self.$target.empty().append(new_qty);
            var model = self.$target.parent().attr('data-oe-model');
            if(model){
              self.$target.parent().addClass('o_editable o_dirty');
            }
          }}, {text: _t('Discard'), close: true}],
          $content: QWeb.render("alan_customize.embeded_block",{'data':markupStr}),
        });
        dialog.open();
        return self;
      }
    },
    onBuilt: function () {
      var self = this;
      this._super();
      this.modify_note("click", "true");
    },
  });
});
