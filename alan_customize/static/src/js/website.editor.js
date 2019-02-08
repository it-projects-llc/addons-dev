odoo.define('alan_customize.editor_js',function(require){
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var weContext = require('web_editor.context');
    var web_editor = require('web_editor.editor');
    var options = require('web_editor.snippets.options');
    var wUtils = require('website.utils');
    var qweb = core.qweb;
    var _t = core._t;

    ajax.loadXML('/alan_customize/static/src/xml/change_progress.xml', core.qweb);
    ajax.loadXML('/alan_customize/static/src/xml/product_template.xml', core.qweb);
    ajax.loadXML('/alan_customize/static/src/xml/product_slider_popup.xml', core.qweb);
    

    options.registry.theme_progressbar = options.Class.extend({
        start : function () {
            var self = this;
            this.id = this.$target.attr("id");
        },
        change_progress: function(type,value) {
            var self = this;
            self.$modal = $(qweb.render("alan_customize.change_progress_modal"));
            self.$modal.appendTo('body');
            self.$modal.modal();
            var $progress_width = self.$modal.find("#progress-width"),
                $sub_data = self.$modal.find("#sub_data");
            $sub_data.on('click', function() {
                if($progress_width.val() && $progress_width.val() >= 0 && $progress_width.val() <= 100){
                    var type = '';
                    self.$target.attr('data-animate-width',$progress_width.val()+'%');
                }
                else{
                    alert("Please enter Progress Value between [0-100]");
                    return false;
                }
            });
            return;
        },
    });

    options.registry.product_brand_slider = options.Class.extend({
        brand_slider_configure: function(type,value) {
            var self= this;
            if(type=="click"  || value===undefined){
                self.$modal = $(qweb.render("alan_customize.brand_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $brand_count = self.$modal.find("#brand-count"),
                    $cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#sub_data"),
                    $brand_label = self.$modal.find("#brand-label");
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr("data-brand-count", $brand_count.val());
                    if ($brand_label.val()) {
                        type = $brand_label.val();
                    } 
                    else {
                        type = "Brands";
                    }
                    self.$target.attr("data-brand-label", type);
                    self.$target.empty().append('<div class="container"><div class="shopper_brand_slider"><div class="col-md-12"><div class="seaction-head"><h1>' + type + '</h1> </div></div></div></div>');
                });
            }
        },
        onBuilt: function () {
            var self = this;
            this._super();
            this.brand_slider_configure("click").fail(function () {
                self.getParent()._onRemoveClick($.Event( "click" ));
            });
        },
        cleanForSave: function () {
            this.$target.empty();
            var model = this.$target.parent().attr('data-oe-model');
            if(model){
                this.$target.parent().addClass('o_editable o_dirty');
            }
        },
    });




    options.registry.product_slider_actions = options.Class.extend({
        product_slider_configure: function(previewMode, value){
            var self = this;
            if(previewMode === false || previewMode === "click"){
                self.$modal = $(qweb.render("alan_customize.p_slider_popup_template"));
                $('body > #product_slider_modal').remove();
                self.$modal.appendTo('body');
                self._rpc({
                    model: 'multitab.configure',
                    method: 'name_search',
                    args: ['', []],
                    context: weContext.get()
                }).then(function(data){
                    var s_tab_ele = $("#product_slider_modal select[name='s_tab_collection']");
                    s_tab_ele.empty();
                    var val_in_list_flag = true;
                    var val_in_list = false;
                    console.log("s_tab_ele", self.$target.attr("data-collection_id"), typeof(self.$target.attr("data-collection_id")));
                    if(data){
                        for(var i = 0; i < data.length; i++){
                            s_tab_ele.append("<option value='" + data[i][0] + "'>" + data[i][1] + "</option>");
                            console.log('-', data[i][0], '-', typeof(data[i][0]));
                            if(data[i][0].toString() === self.$target.attr("data-collection_id") && val_in_list_flag){
                                val_in_list = true;
                                val_in_list_flag = false;
                            }
                        }
                        if(self.$target.attr("data-collection_id") !== "0" && val_in_list && self.$target.attr("data-snippet_type") === "single"){
                            s_tab_ele.val(self.$target.attr("data-collection_id"));
                        }
                    }
                    self._rpc({
                        model: 'collection.configure',
                        method: 'name_search',
                        args: ['', []],
                        context: weContext.get()
                    }).then(function(data){
                        var m_tab_ele = $("#product_slider_modal select[name='m_tab_collection']");
                        m_tab_ele.empty();
                        val_in_list_flag = true;
                        val_in_list = false;
                        if(data){
                            console.log("m_tab_ele", self.$target.attr("data-collection_id"));
                            for(var i = 0; i < data.length; i++){
                                m_tab_ele.append("<option value='" + data[i][0] + "'>" + data[i][1] + "</option>");
                                if(data[i][0].toString() === self.$target.attr("data-collection_id") && val_in_list_flag){
                                    val_in_list = true;
                                    val_in_list_flag = false;
                                }
                            }
                            if(val_in_list && self.$target.attr("data-collection_id") !== "0" && val_in_list && self.$target.attr("data-snippet_type") === "multi"){
                                m_tab_ele.val(self.$target.attr("data-collection_id"));
                            }
                        }
                    });
                });
                self.$modal.on('change', self.$modal.find("select[name='slider_type']"), function(){
                    var $sel_ele = $(this).find("select[name='slider_type']");
                    var $form = $(this).find("form");
                    if($sel_ele.val() === "single"){
                        $form.find(".s_tab_collection_container").show();
                        $form.find(".m_tab_collection_container").hide();                                               

                    }
                    else if($sel_ele.val() === "multi"){
                        $form.find(".s_tab_collection_container").hide();
                        $form.find(".m_tab_collection_container").show();
                    }
                    else{ console.log("JS is compromised!"); }
                });
                self.$modal.on('change', self.$modal.find("select[name='s_tab_layout'],select[name='m_tab_layout']"), function(e){
                    var $sel_ele;
                    var val_list = [];
                    if(self.$modal.find("select[name='slider_type']").val() === 'single')
                        $sel_ele = self.$modal.find("select[name='s_tab_layout']");
                    else if(self.$modal.find("select[name='slider_type']").val() === 'multi')
                        $sel_ele = self.$modal.find("select[name='m_tab_layout']");
                    else{ console.log("Element not found!"); return; }
                    self.$modal.find("form .p_slider_sample_view img.snip_sample_img").attr("src", "/alan_customize/static/src/img/snippets/" + $sel_ele.val() + ".png");
                    
                });
                // self.$modal.
                self.$modal.on('click', ".btn_apply", function(){
                    var $sel_ele = self.$modal.find("select[name='slider_type']");
                    var $form = self.$modal.find("form");
                    var collection_name = '';

                    if($sel_ele.val() === "single"){

                        collection_name = $form.find("select[name='s_tab_collection'] option:selected").text();
                        if(!collection_name)
                            collection_name = "NO COLLECTION SELECTED";
                        self.$target.attr('data-snippet_type', $sel_ele.val());
                        self.$target.attr("data-collection_id", $form.find("select[name='s_tab_collection']").val());
                        self.$target.attr("data-collection_name", collection_name);
                        self.$target.attr("data-snippet_layout", $form.find("select[name='s_tab_layout']").val());
                    }
                    else if($sel_ele.val() === "multi"){

                        collection_name = $form.find("select[name='m_tab_collection'] option:selected").text();
                        if(!collection_name)
                            collection_name = "NO COLLECTION SELECTED";
                        self.$target.attr('data-snippet_type', $sel_ele.val());
                        self.$target.attr("data-collection_id", $form.find("select[name='m_tab_collection']").val());
                        self.$target.attr("data-collection_name", collection_name);
                        self.$target.attr("data-snippet_layout", $form.find("select[name='m_tab_layout']").val());
                    }
                    else{
                        collection_name = 'NO COLLECTION SELECTED';
                    }
                    self.$target.empty().append('<div class="container"><div class="seaction-head"><h2>' + collection_name + '</h2></div></div>');
                });
                var sn_type = self.$target.attr("data-snippet_type");
                var sn_col = self.$target.attr("data-collection_id");
                var sn_layout = self.$target.attr("data-snippet_layout");

                if(sn_type !== "0" && sn_layout !== "0" && sn_col !== "0"){
                    self.$modal.find("form select[name='slider_type']").val(sn_type);
                    if(self.$target.attr("data-snippet_type") === "single"){
                        self.$modal.find("form select[name='s_tab_layout']").val(sn_layout);
                    }
                    else if(self.$target.attr("data-snippet_type") === "multi"){
                        self.$modal.find("form select[name='m_tab_layout']").val(sn_layout);
                    }
                    else{ 
                    }
                    
                }
                self.$modal.find("select[name='slider_type']").trigger("change");
                self.$modal.modal();
            }
            return self;
        },
        onBuilt: function(){
            var self = this;
            this._super();
            this.product_slider_configure('click');
        }
    });

});
