odoo.define('pos_restaurant.printer_status', function (require) {
    "use strict";

    var multiprint = require('pos_restaurant.multiprint');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var Session = require('web.Session');


    var QWeb = core.qweb;
    var mixins = core.mixins;

    core.Class.extend(mixins.PropertiesMixin,{
        print: function(receipt){
            console.log("before");
            mixins.PropertiesMixin.print.call(this);
            console.log("after");
            // var self = this;
            // if(receipt){
            //     this.receipt_queue.push(receipt);
            // }
            // function send_printing_job(){
            //     if(self.receipt_queue.length > 0){
            //         console.log("PRINTER: ", this.config.name);
            //         console.log("STATUS: IN PROGRESS");
            //         var r = self.receipt_queue.shift();
            //         self.connection.rpc('/hw_proxy/print_xml_receipt',{receipt: r},{timeout: 5000})
            //             .then(function(){
            //                 console.log("STATUS: PRINTING IS DONE");
            //                 send_printing_job();
            //             },function(){
            //                 console.log("STATUS: PRINTING IS FAILED");
            //                 self.receipt_queue.unshift(r);
            //             });
            //     }
            // }
            // send_printing_job();
        },
    });

    var PrinterStatusButton = screens.ActionButtonWidget.extend({
        template: 'PrinterStatusButton',
        button_click: function(){
            var self = this;
            this.gui.show_screen('printerstatuslist');
        },

    });
    screens.define_action_button({
        'name': 'printer_status',
        'widget': PrinterStatusButton,
        'condition': function() {
            return this.pos.printers.length;
        },
    });

    var PrinterStatusScreenWidget = screens.ScreenWidget.extend({
        template: 'PrinterStatusScreenWidget',
        init: function(parent, options){
            this._super(parent, options);
            this.printer_status_cache = new screens.DomCache();
            this.printer_set_status_cache = new screens.DomCache();
        },
        auto_back: true,
        show: function(){
            var self = this;
            this._super();
            this.selected_printers_id = [];
            this.current_printer_id = [];
            this.details_visible = false;
            this.renderElement();
            this.printers_option = [];

            this.pos.printers.forEach(function(printer){
                self.printers_option.push({
                    'name': printer.config.name,
                    'status': 'running',
                    'id': printer.config.id,
                    'clicked': false,
                    'info': [],
                })
            });

            this.$('.back').click(function(){
                self.gui.back();
            });
            this.render_list(self.printers_option);

            this.$('.printer-list-contents').delegate('.printer-line','click',function(event){
                self.select_printer_list(event,$(this),parseInt($(this).data('id')));
            });
        },
        select_printer_list: function(event,$line,id) {
            var self = this;
            this.printers_option.forEach(function(printer){
                if (printer.id == id) {
                    if (printer.clicked) {
                        printer.clicked = false;
                    }else {
                        printer.clicked = true;
                    }
                    self.add_info(printer);
                }
            });
            this.render_list(self.printers_option);
        },
        add_info: function(printer){
            console.log("add info for printer");
            printer.info.push({'name': 'set1', 'status': 'running'});
            printer.info.push({'name': 'set2', 'status': 'running'});
        },
        hide: function () {
            this._super();
        },
        render_list: function(printers){
            console.log(printers);
            var contents = this.$el[0].querySelector('.printer-list-contents');
            contents.innerHTML = "";
            for(var i = 0, len = Math.min(printers.length,1000); i < len; i++){
                var printer    = printers[i];
                var printerline_html = QWeb.render('PrinterLine',{widget: this, printer:printers[i]});
                var printerline = document.createElement('tbody');
                printerline.innerHTML = printerline_html;
                printerline = printerline.childNodes[1];
                this.printer_status_cache.cache_node(printer.id,printerline);
                contents.appendChild(printerline);
            }
        },
        toggle_save_button: function(){
            var $button = this.$('.button.next');
            var self = this;
            if (this.selected_lines_id.length !== 0) {
                $button.removeClass('oe_hidden');
                $button.text(_t('Apply'));
            } else {
                $button.addClass('oe_hidden');
                self.display_note('hide');
            }
        },
        line_select: function(event,$line,id){
            if ( $line.hasClass('highlight') ){
                $line.removeClass('highlight');
                var line_id = this.selected_lines_id.indexOf(id);
                if (line_id !== -1) {
                    this.selected_lines_id.splice(line_id, 1);
                }
            }else {
                this.$('.product-line .highlight').removeClass('highlight');
                $line.addClass('highlight');
                this.selected_lines_id.push(id);
                var y = event.pageY - $line.parent().offset().top;
                this.display_note('show',y);
            }
            this.toggle_save_button();
        },
        display_note: function(visibility, clickpos){
            var self = this;
            var contents = this.$('.cancellation-reason-contents');
            var parent   = this.$('.order-product-list').parent();
            var scroll   = parent.scrollTop();
            var height   = contents.height();
            if(visibility === 'show'){
                var new_height   = contents.height();
                if(!this.details_visible){
                    contents.empty();
                    contents.append($(QWeb.render('CancellationReason',{widget:this})));
                    if(clickpos < scroll + new_height + 20 ){
                        parent.scrollTop( clickpos - 20 );
                    }else{
                        parent.scrollTop(parent.scrollTop() + new_height);
                    }
                }else{
                    parent.scrollTop(parent.scrollTop() - height + new_height);
                }
                this.details_visible = true;
            } else if (visibility === 'hide') {
                contents.empty();
                if( height > scroll ){
                    contents.css({height:height+'px'});
                    contents.animate({height:0},400,function(){
                        contents.css({height:''});
                    });
                }else{
                    parent.scrollTop( parent.scrollTop() - height);
                }
                this.details_visible = false;
            }
        },
        close: function(){
            this._super();
        },
    });
    gui.define_screen({name:'printerstatuslist', widget: PrinterStatusScreenWidget});

    // models.load_models({
    //     model: 'restaurant.printer',
    //     fields: ['printer_method_name'],
    //     domain: null,
    //     loaded: function(self,printers){
    //         self.printers.forEach(function(item){
    //             var printer_obj = printers.find(function(printer){
    //                 return printer.id == item.config.id;
    //             });
    //             item.config.printer_method_name = printer_obj.printer_method_name;
    //         });
    //     },
    // });
    //
    // var OrderSuper = models.Order;
    // models.Order = models.Order.extend({
    //     printChanges: function(){
    //         var self = this;
    //         var printers = this.pos.printers;
    //         for(var i = 0; i < printers.length; i++){
    //             var changes = this.computeChanges(printers[i].config.product_categories_ids);
    //             if ( changes['new'].length > 0 || changes['cancelled'].length > 0){
    //                 if (printers[i].config.printer_method_name == 'separate_receipt') {
    //                     var changes_new = $.extend({}, changes);
    //                     changes_new.new.forEach(function(orderline){
    //                         changes_new.cancelled = [];
    //                         changes_new.new = [orderline];
    //                         self.render_order_receipt(printers[i], changes_new);
    //                     });
    //                     var changes_cancelled= $.extend({}, changes);
    //                     changes_cancelled.cancelled.forEach(function(orderline){
    //                         changes_cancelled.cancelled = [orderline];
    //                         changes_cancelled.new = [];
    //                         self.render_order_receipt(printers[i], changes_cancelled);
    //                     });
    //                 } else {
    //                     self.render_order_receipt(printers[i], changes);
    //                 }
    //             }
    //         }
    //     },
    //     render_order_receipt: function(printers, changes) {
    //         var receipt = QWeb.render('OrderChangeReceipt',{changes:changes, widget:this});
    //         printers.print(receipt);
    //     },
    // });
});
