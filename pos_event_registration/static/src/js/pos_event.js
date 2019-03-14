/*  Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */
odoo.define('pos_event_registration.pos_event', function (require) {
"use strict";

//var bus = require('bus.bus');
//var local_storage = require('web.local_storage');

var Session = require('web.session');
var screens = require('point_of_sale.screens');
var models = require('point_of_sale.models');
var devices = require('point_of_sale.devices');
var gui = require('point_of_sale.gui');
var core = require('web.core');
var PosDB = require('point_of_sale.DB');
var rpc = require('web.rpc');

var QWeb = core.qweb;
var _t = core._t;


models.load_models({
    model: 'pos.event.set',
    fields: ['name', 'pos_ticket_ids'],
    ids:    function(self){
        return self.config.pos_event_set_id && [self.config.pos_event_set_id[0]];
    },
    loaded: function(self, event_set){
        self.event_set = {};
        if (event_set && event_set.length) {
            _.extend(self.event_set, event_set[0]);
        }
    },
});
models.load_models({
    model: 'pos.event.ticket',
    fields: ['name', 'product_id', 'ask_for_rfid', 'event_id', 'ticket_id',],
    ids:    function(self){
        return self.event_set && self.event_set.pos_ticket_ids;
    },
    loaded: function(self, pos_tickets){
        if (pos_tickets && pos_tickets.length) {
            self.event_set.event_ids = [];
            self.event_set.pos_ticket_ids = {};
            _.each(pos_tickets, function(t){
                self.event_set.pos_ticket_ids[t.id] = t;
                self.event_set.event_ids.push(t.event_id[0]);
            });
        }
    },
});
models.load_models({
    model: 'event.event',
    fields: ['name', 'event_ticket_ids'],
    ids:    function(self){
        return _.unique(self.event_set.event_ids);
    },
    loaded: function(self, events){
        self.event_set.event_ids = {};
        _.each(events, function(e){
            self.event_set.event_ids[e.id] = e;
        });
    },
});
models.load_models({
    model: 'event.registration',
    fields: ['id', 'name', 'partner_id', 'attendee_partner_id', 'date_open', 'state', 'email', 'state', 'event_ticket_id', 'barcode', 'rfid', 'event_id'],
    domain: function(self){
        var event_ids = _.chain(self.event_set.event_ids)
        .keys()
        .map(function(e){
            return parseInt(e);
        }).value();
        return [['event_id', 'in', event_ids]];
    },
    loaded: function(self, attendees){
        self.db.attendees = attendees;
        self.db.attendee_by_id = {};
        self.db.attendee_sorted = [];
        _.each(attendees, function(a){
            self.db.attendee_by_id[a.id] = a;
            self.db.attendee_sorted.push(a);
        });
        self.db.ticket_customers_ids = _.filter(_.unique(_.map(attendees, function(a){
            return a.partner_id[0];
        })), function(p){
            return p;
        });
    },
});
models.load_models({
    // adds ticket customers as partners
    model: 'res.partner',
    fields: ['name','street','city','state_id','country_id','vat','phone','zip','mobile','email','barcode','write_date','property_account_position_id'],
    ids:    function(self){
        return self.config.pos_event_set_id
         ? _.difference(self.db.ticket_customers_ids, self.db.partner_sorted)
            // difference excludes already downloaded partners
         : [];
    },
    loaded: function(self, partners){
        self.db.add_partners(partners);
    },
});
models.load_models({
    model: 'event.event.ticket',
    fields: ['id', 'name', 'event_id', 'product_id', 'registration_ids', 'price'],
    ids:    function(self){
        return self.get_event_ticket_data_ids('ticket_id');
    },
    loaded: function(self, tickets){
        self.db.tickets = tickets;
        self.db.tickets_by_id = [];
        _.each(tickets, function(t) {
            self.db.tickets_by_id[t.id] = t;
        });
    },
});
models.load_models({
    model:  'product.product',
    fields: ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'barcode', 'default_code',
             'to_weight', 'uom_id', 'description_sale', 'description','event_ticket_ids', 'event_ok',
             'product_tmpl_id','tracking', 'categ_id'],
    order:  ['sequence','default_code','name'],
    ids:    function(self){
        return self.get_event_ticket_data_ids('product_id');
    },
    loaded: function(self, products){
        //copy-pasted from odoo
        _.each(products, function(p){
            p.price = p.list_price;
        });
        var using_company_currency = self.config.currency_id[0] === self.company.currency_id[0];
        var conversion_rate = self.currency.rate / self.company_currency.rate;
        self.db.add_products(_.map(products, function (product) {
            if (!using_company_currency) {
                product.lst_price = round_pr(product.lst_price * conversion_rate, self.currency.rounding);
            }
            product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
            return new models.Product({}, product);
        }));
    },
});


devices.BarcodeReader.include({
    scan: function(code){
        var attendeelist = this.pos.gui.screen_instances.attendeelist;
        if (!this.pos.gui.current_screen.attendee_screen) {
            var attendee = this.pos.db.get_attendee_by_barcode(code);
            if (attendee) {
                return this.show_attendee_in_list(attendee);
            }
            return this._super(code);
        }
        var parsed_result = this.barcode_parser.parse_barcode(code);
        attendeelist.barcode_attendee_action(parsed_result);
    },

    show_attendee_in_list: function(attendee){
        var attendeelist = this.pos.gui.screen_instances.attendeelist;
        this.pos.gui.show_screen('attendeelist');
        attendeelist.display_client_details('show',attendee);
        attendeelist.current_attendee = attendee;
    },
});

screens.ProductListWidget.include({
    set_product_list: function(product_list){
        // filters out non ticket products TODO: make it customizable
        var product_ids = this.pos.get_event_ticket_data_ids('product_id');
        if (this.pos.config.pos_event_set_id && this.pos.config.show_only_tickets) {
            var self = this;
            product_list = _.filter(product_list, function(p){
                return _.includes(product_ids, p.id);
            });
        }
        return this._super(product_list);
    },
});


var PosModelSuper = models.PosModel;
models.PosModel = models.PosModel.extend({
    initialize: function(){
        var self = this;
        PosModelSuper.prototype.initialize.apply(this, arguments);
        this.ready.then(function () {
            self.bus.add_channel_callback("pos_attendee_update", self.on_attendee_updates, self);
        });
    },

    load_new_attendees: function(ids){
        var self = this;
        var def = new $.Deferred();
        var request = new $.Deferred();
        var fields = _.find(this.models,function(model){
            return model.model === 'event.registration';
        }).fields;
        if (ids) {
            // call: function (method, args, kwargs, options) {
            ids = Array.isArray(ids)
            ? ids
            : [ids];
            request = rpc.query({
                model: 'event.registration',
                method: 'read',
                args: [ids, fields, {}, {'shadow': true}],
            });
        } else {
            // call: function (method, args, kwargs, options) {
            request = rpc.query({
                model: 'event.registration',
                method: 'search_read',
//                args: [['event_id', '=', this.get_event_ticket_data_ids('event_id')], fields, {}, {'shadow': true}],
                args: [[['event_id', '=', this.get_event_ticket_data_ids('event_id')]], fields],
            });
        }
        request.then(function(attendees){
            if (self.db.add_attendees(attendees)) {
                // check if the attendees we got were real updates
                def.resolve();
            } else {
                def.reject();
            }
        }, function(err,event){
            if (err) {
                console.log(err.stack);
            }
            event.preventDefault();
            def.reject();
        });
        return def;
    },

    on_attendee_updates: function(data) {
        var self = this;
        this.load_new_attendees(data.attendees).then(function(){
            self.trigger('changed:attendee', data);
        });
    },

    open_record_in_backend: function(model, id){
        var url = this.config.web_url + id + "&view_type=form&model=" + model;
        var win = window.open(url, '_blank');
        win.focus();
    },

    has_tickets: function() {
        var self = this;
        var orderlines = this.get_order().get_orderlines();

        return _.find(orderlines, function(ol){
            return _.contains(self.get_event_ticket_data_ids('product_id'), ol.product.id);
        });
    },
    get_event_ticket_data_ids: function(key){
        var pos_ticket_ids = this.event_set.pos_ticket_ids;
        return pos_ticket_ids
        ? _.chain(pos_ticket_ids)
            .map(key)
            .map('0')
            .map(function(i){
                return parseInt(i);
            })
            .unique().value()
        : [];
    },
    get_event_ticket_by_attr_id: function(key, id){
        var pos_ticket_ids = this.event_set.pos_ticket_ids;
        return _.find(pos_ticket_ids, function(t){
            return t[key][0] === id;
        });
    },
});

PosDB.include({

    /* TICKETS */

    get_ticket_by_id: function(id){
        return this.tickets[id];
    },

    /* ATTENDEE */

    get_attendees_sorted: function(max_count){
        max_count = max_count
        ? Math.min(this.attendee_sorted.length, max_count)
        : this.attendee_sorted.length;
        var attendees = [];
        for (var i = 0; i < max_count; i++) {
            attendees.push(this.attendee_by_id[this.attendee_sorted[i].id]);
        }
        return attendees;
    },
    get_attendee_by_id: function(id){
        return this.attendee_by_id[id];
    },
    get_attendee_by_barcode: function(barcode) {
        return _.find(this.attendees, function(a){
            return a.barcode && a.barcode === barcode;
        });
    },
    get_attendee_by_partner_id: function(partner_id) {
        return _.find(this.attendees, function(i){
            return i.partner_id[0] === partner_id;
        });
    },

    add_attendees: function(attendees){
        var updated_count = 0;
        var new_write_date = '';
        var self = this;
        var attendee = false;
        for(var i = 0, len = attendees.length; i < len; i++){
            attendee = attendees[i];

            if (!this.attendee_by_id[attendee.id]) {
                this.attendee_sorted.push(attendee);
            }
            this.attendee_by_id[attendee.id] = attendee;

            updated_count += 1;
            var db_attendee = _.find(this.attendees, function(a){
                return a.id === attendee.id;
            });

            if (!db_attendee) {
                this.attendees.push(attendee);
            }
        }

        if (updated_count) {
            // If there were updates, we need to completely
            // rebuild the search string and the barcode indexing

            this.attendee_search_string = "";
            this.attendee_by_barcode = {};

            _.chain(this.attendee_by_id)
                .keys('product')
                .each(function(id){
                    attendee = self.attendee_by_id[parseInt(id)];
                    if(attendee.barcode){
                        self.attendee_by_barcode[attendee.barcode] = attendee;
                    }
                    self.attendee_search_string += self._attendee_search_string(attendee);
                }).value();
        }
        return updated_count;
    },

    _attendee_search_string: function(attendee){
        var str = attendee.name;
        if(attendee.barcode){
            str += '|' + attendee.barcode;
        }
        if(attendee.partner_id){
            str += '|' + attendee.partner_id[1];
        }
        if(attendee.email){
            str += '|' + attendee.email.split(' ').join('');
        }
        str = '' + String(attendee.id) + ':' + str.replace(':','') + '\n';
        return str;
    },

    search_attendee: function(query){
        try {
            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
            query = query.replace(/ /g,'.+');
            var re = RegExp("([0-9]+):.*?"+query,"gi");
        } catch(e) {
            return [];
        }
        var results = [];
        for (var i = 0; i < this.limit; i++) {
            var r = re.exec(this.attendee_search_string);
            if (r) {
                var id = Number(r[1]);
                results.push(this.get_attendee_by_id(id));
            } else {
                break;
            }
        }
        return results;
    },

});

screens.PaymentScreenWidget.include({

    validate_order: function(options) {
        if (this.pos.has_tickets()) {
            var currentOrder = this.pos.get_order();
            var client = currentOrder.get_client();
            if (!client){
                this.gui.show_popup('error',{
                    'title': _t('Unknown customer'),
                    'body': _t('You cannot sell a ticket with unselected customer. Create / Select customer first.'),
                });
                return;
            } else if (!client.email) {
                this.gui.show_popup('error',{
                    'title': _t('Customers email is not set'),
                    'body': _t('You cannot sell a ticket to a customer with unspecified email.'),
                });
                return;
            }
            /*var attendee = this.check_partner_is_attendee(client);
            if (attendee) {
                this.gui.show_popup('error',{
                    'title': _t('Customer has a Ticket'),
                    'body': _t('You cannot sell multiple tickets to the same person.'),
                });
                return;
            }*/
            if (this.check_for_multiple_tickets()){
                this.gui.show_popup('error',{
                    'title': _t('Multiple tickets per customer'),
                    'body': _t('Unable to buy several tickets on the same event for the same partner.'),
                });
                return;
            }
        }
        var res = this._super(options);
        return res;
    },

    check_partner_is_attendee: function (partner) {
        return _.find(this.pos.db.attendees, function(a){
            return a.partner_id[0] === partner.id;
        });
    },

    check_for_multiple_tickets: function() {
        var self = this;
        var result = false;
        var ticket = false;
        var same_product_lines = false;
        var orderlines = this.pos.get_order().get_orderlines();
        var products = _.chain(orderlines)
            .pluck('product')
            .pluck('id')
            .unique().value();
        _.each(products, function(pr_id){
            ticket = self.pos.get_event_ticket_by_attr_id('product_id', pr_id);
            if (ticket) {
                same_product_lines = _.filter(orderlines, function(ol){
                    if (ol.product.id === pr_id) {
                        return true;
                    }
                });
                if (same_product_lines.length > 1 || (same_product_lines.length === 1 && same_product_lines[0].quantity > 1)){
                    result = true;
                }
            }
        });
        return result;
    },
});


/*--------------------------------------*\
 |           ATTENDEE LIST              |
\*======================================*/

var AttendeeListScreenWidget = screens.ScreenWidget.extend({
    template: 'AttendeeListScreenWidget',

    auto_back: true,
    attendee_screen: true,

    init: function(parent, options){
        this._super(parent, options);
        this.attendee_cache = new screens.DomCache();

    },


    get_attendee: function() {
        return this.current_attendee;
    },
    set_attendee: function(attendee) {
        this.current_attendee = attendee;
        return attendee;
    },

    show: function(){
        var self = this;
        this._super();

        this.renderElement();
        this.details_visible = false;
        var client = this.pos.get_client();
        this.old_attendee = this.pos.db.get_attendee_by_partner_id(client && client.id);

        this.$('.back').click(function(){
            self.gui.back();
        });

        /* distracts users
        this.$('.next').click(function(){
            self.save_changes();
            self.gui.back();
        });*/

        var attendees = this.pos.db.get_attendees_sorted(1000);
        this.render_list(attendees);

        this.reload_attendees();

        if( this.old_attendee ){
            this.display_client_details('show',this.old_attendee,0);
        }

        this.$('.client-list-contents').delegate('.client-line','click',function(event){
            self.line_select(event,$(this),parseInt($(this).data('id')));
        });

        var search_timeout = null;

        if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
            this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
        }

        this.$('.searchbox input').on('keypress',function(event){
            clearTimeout(search_timeout);

            var searchbox = this;

            search_timeout = setTimeout(function(){
                self.perform_search(searchbox.value, event.which === 13);
            },70);
        });

        this.$('.searchbox .search-clear').click(function(){
            self.clear_search();
        });

        this.pos.barcode_reader.set_action_callback({
            'attendee': _.bind(self.barcode_attendee_action, self),
        });

        var $button_attendee = this.$('.button.attendeed.highlight');
        $button_attendee.on('click', function(e){
            self.validate_attendee();
        });
    },


    hide: function () {
        this._super();
        this.current_attendee = null;
    },

    validate_attendee: function() {
        var self = this;

        if (!this.check_for_rfid()) {
            self.gui.show_popup('error',{
                'title': _t('Error: Could not Accept Attendee'),
                'body': 'RFID is not set',
            });
            return false;
        }

        return rpc.query({
            model: 'event.registration',
            method: 'register_attendee_from_ui',
            args: [self.current_attendee.id],
        }).then(function(attendee_id){
            self.saved_client_details(attendee_id);
        },function(err,event){
            event.preventDefault();
            var error_body = _t('Your Internet connection is probably down.');
            if (err.data) {
                var except = err.data;
                error_body = (except.arguments && except.arguments[0]) || except.message || error_body;
            }
            self.gui.show_popup('error',{
                'title': _t('Error: Could not Save Changes'),
                'body': error_body,
            });
        });
    },
    check_for_rfid: function() {
        var self = this;
        var attendee_event_id = this.current_attendee.event_id[0];
        var attendee_ticket = this.pos.get_event_ticket_by_attr_id('event_id', attendee_event_id);
        return this.current_attendee.rfid || !attendee_ticket.ask_for_rfid;
    },

    barcode_attendee_action: function(parsed_result){
        var code = parsed_result.code;
        var attendee = this.pos.db.get_attendee_by_barcode(code);
        if (attendee) {
            this.current_attendee = attendee;
            this.display_client_details('show', attendee);
        } else if (this.current_attendee) {
            this.current_attendee.rfid = code;
            this.display_client_details('show', this.current_attendee);
            this.save_client_details(this.current_attendee);
            this.render_list(this.pos.db.get_attendees_sorted(1000));
        }
    },

    perform_search: function(query, associate_result){
        var customers = false;
        if(query){
            customers = this.pos.db.search_attendee(query);
            this.display_client_details('hide');
            if ( associate_result && customers.length === 1){
                this.current_attendee = customers[0];
                this.save_changes();
                this.gui.back();
            }
            this.render_list(customers);
        }else{
            customers = this.pos.db.get_attendees_sorted();
            this.render_list(customers);
        }
    },
    clear_search: function(){
        var customers = this.pos.db.get_attendees_sorted(1000);
        this.render_list(customers);
        this.$('.searchbox input')[0].value = '';
        this.$('.searchbox input').focus();
    },
    render_list: function(attendees){
        var contents = this.$el[0].querySelector('.client-list-contents');
        contents.innerHTML = "";
        for(var i = 0, len = Math.min(attendees.length,1000); i < len; i++){
            var attendee = attendees[i];
            // TODO: why here comes undefined attendeees?
            // 'continue' is a lint
            if (attendee){
                var clientline = this.attendee_cache.get_node(attendee.id);
                if(!clientline){
                    var clientline_html = QWeb.render('AttendeeLine',{widget: this, attendee:attendees[i]});
                    clientline = document.createElement('tbody');
                    clientline.innerHTML = clientline_html;
                    clientline = clientline.childNodes[1];
                    this.attendee_cache.cache_node(attendee.id,clientline);
                }
                if( attendee === this.old_attendee ){
                    clientline.classList.add('highlight');
                }else{
                    clientline.classList.remove('highlight');
                }
                contents.appendChild(clientline);
            }
        }
    },
    save_changes: function(){
        var self = this;
        var order = this.pos.get_order();
        if( this.has_client_changed() ){
            var default_fiscal_position_id = _.find(this.pos.fiscal_positions, function(fp) {
                return fp.id === self.pos.config.default_fiscal_position_id[0];
            });
            if ( this.current_attendee && this.current_attendee.property_account_position_id ) {
                order.fiscal_position = _.find(this.pos.fiscal_positions, function (fp) {
                    return fp.id === self.current_attendee.property_account_position_id[0];
                }) || default_fiscal_position_id;
            } else {
                order.fiscal_position = default_fiscal_position_id;
            }

            order.set_client(this.current_attendee);
        }
    },
    has_client_changed: function(){
        if( this.old_attendee && this.current_attendee ){
            return this.old_attendee.id !== this.current_attendee.id;
        }
            return Boolean(this.old_attendee) !== Boolean(this.current_attendee);
    },
    toggle_save_button: function(){
        var $button = this.$('.button.next');
        if (this.editing_client) {
            $button.addClass('oe_hidden');
            return;
        } else if( this.current_attendee ){
            if(this.old_attendee){
                $button.text(_t('Change Customer'));
            }else{
                $button.text(_t('Set Customer'));
            }
        }else{
            $button.text(_t('Deselect Customer'));
        }
        $button.toggleClass('oe_hidden',!this.has_client_changed());

        this.action_show_attendeed_button();
    },
    action_show_attendeed_button: function(){
        var $button_attendee = this.$('.button.attendeed.highlight');
        if (this.current_attendee && this.current_attendee.state === 'open') {
            $button_attendee.show();
        } else {
            $button_attendee.hide();
        }
    },
    line_select: function(event,$line,id){
        var attendee = this.pos.db.get_attendee_by_id(id);
        this.$('.client-list .lowlight').removeClass('lowlight');
        if ( $line.hasClass('highlight') ){
            $line.removeClass('highlight');
            $line.addClass('lowlight');
            this.display_client_details('hide',attendee);
            this.current_attendee = null;
            this.toggle_save_button();
        }else{
            this.$('.client-list .highlight').removeClass('highlight');
            $line.addClass('highlight');
            var y = event.pageY - $line.parent().offset().top;
            this.current_attendee = attendee;
            this.display_client_details('show',attendee,y);
            this.toggle_save_button();
        }
    },
    attendee_icon_url: function(id){
        return '/web/image?model=event.registration&id='+id+'&field=image_small';
    },

    // ui handle for the 'edit selected customer' action
    edit_client_details: function(attendee) {
        this.display_client_details('edit',attendee);
    },

    // ui handle for the 'cancel customer edit changes' action
    undo_client_details: function(attendee) {
        if (attendee.id) {
            this.display_client_details('show',attendee);
        } else {
            this.display_client_details('hide');
        }
    },

    // what happens when we save the changes on the client edit form -> we fetch the fields, sanitize them,
    // send them to the backend for update, and call saved_client_details() when the server tells us the
    // save was successfull.
    save_client_details: function(attendee) {
        var self = this;

        var fields = {};
        if (this.editing_client) {
            this.$('.client-details-contents .detail').each(function(idx,el){
                fields[el.name] = el.value || false;
            });
            if (!fields.name) {
                this.gui.show_popup('error',_t('A Customer Name Is Required'));
                return;
            }

        } else {
            this.$('.client-details-contents .field').each(function(idx,el){
                fields[el.getAttribute('name')] = el.innerHTML || false;
            });
        }


        fields.id = attendee.id || false;
        fields.country_id = fields.country_id || false;
        fields.session_id = this.pos.pos_session.id;
        fields.event_id = attendee.event_id[0];
        rpc.query({
            model: 'event.registration',
            method: 'create_from_ui',
            args: [fields],
        }).then(function(attendee_id){
            self.saved_client_details(attendee_id);
        },function(err,event){
            event.preventDefault();
            var error_body = _t('Your Internet connection is probably down.');
            if (err.data) {
                var except = err.data;
                error_body = (except.arguments && except.arguments[0]) || except.message || error_body;
            }
            self.gui.show_popup('error',{
                'title': _t('Error: Could not Save Changes'),
                'body': error_body,
            });
        });
    },

    // what happens when we've just pushed modifications for a attendee of id attendee_id
    saved_client_details: function(attendee_id){
        var self = this;
        return this.reload_attendees(attendee_id).then(function(){
            var attendee = self.pos.db.get_attendee_by_id(attendee_id);
            if (attendee) {
                self.current_attendee = attendee;
                self.toggle_save_button();
                self.display_client_details('show',attendee);
            } else {
                // should never happen, because create_from_ui must return the id of the attendee it
                // has created, and reload_attendee() must have loaded the newly created attendee.
                self.display_client_details('hide');
            }
        });
    },

    // resizes an image, keeping the aspect ratio intact,
    // the resize is useful to avoid sending 12Mpixels jpegs
    // over a wireless connection.
    resize_image_to_dataurl: function(img, maxwidth, maxheight, callback){
        img.onload = function(){
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            var ratio = 1;

            if (img.width > maxwidth) {
                ratio = maxwidth / img.width;
            }
            if (img.height * ratio > maxheight) {
                ratio = maxheight / img.height;
            }
            var width = Math.floor(img.width * ratio);
            var height = Math.floor(img.height * ratio);

            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img,0,0,width,height);

            var dataurl = canvas.toDataURL();
            callback(dataurl);
        };
    },

    // Loads and resizes a File that contains an image.
    // callback gets a dataurl in case of success.
    load_image_file: function(file, callback){
        var self = this;
        if (!file.type.match(/image.*/)) {
            this.gui.show_popup('error',{
                title: _t('Unsupported File Format'),
                body: _t('Only web-compatible Image formats such as .png or .jpeg are supported'),
            });
            return;
        }

        var reader = new FileReader();
        reader.onload = function(event){
            var dataurl = event.target.result;
            var img = new Image();
            img.src = dataurl;
            self.resize_image_to_dataurl(img,800,600,callback);
        };
        reader.onerror = function(){
            self.gui.show_popup('error',{
                title :_t('Could Not Read Image'),
                body  :_t('The provided file could not be read due to an unknown error'),
            });
        };
        reader.readAsDataURL(file);
    },

    // This fetches attendee changes on the server, and in case of changes,
    // rerenders the affected views
    reload_attendees: function(ids){
        var self = this;
        return this.pos.load_new_attendees(ids).then(function(){
            // attendees may have changed in the backend
            self.attendee_cache = new screens.DomCache();

            self.render_list(self.pos.db.get_attendees_sorted(1000));
        });
    },

    // Shows,hides or edit the customer details box :
    // visibility: 'show', 'hide' or 'edit'
    // attendee:    the attendee object to show or edit
    // clickpos:   the height of the click on the list (in pixel), used
    //             to maintain consistent scroll.
    display_client_details: function(visibility,attendee,clickpos){
        var self = this;
        var searchbox = this.$('.searchbox input');
        var contents = this.$('.client-details-contents');
        var parent = this.$('.client-list').parent();
        var scroll = parent.scrollTop();
        var height = contents.height();

        contents.off('click','.button.edit');
        contents.off('click','.button.save');
        contents.off('click','.button.undo');
        contents.on('click','.button.edit',function(){
            self.edit_client_details(attendee);
        });
        contents.on('click','.button.save',function(){
            self.save_client_details(attendee);
        });
        contents.on('click','.button.undo',function(){
            self.undo_client_details(attendee);
        });
        this.editing_client = false;
        this.uploaded_picture = null;

        if(visibility === 'show'){
            contents.empty();
            var related_partner = this.pos.db.get_partner_by_id(attendee.partner_id[0]);
            contents.append($(QWeb.render('AttendeeDetails',{
                widget:this,
                attendee:attendee,
                partner: related_partner,
            })));

            var new_height = contents.height();

            if(this.details_visible){
                parent.scrollTop(parent.scrollTop() - height + new_height);
            }else{
                // resize client list to take into account client details
                parent.height('-=' + new_height);

                if(clickpos < scroll + new_height + 20 ){
                    parent.scrollTop( clickpos - 20 );
                }else{
                    parent.scrollTop(parent.scrollTop() + new_height);
                }
            }

            this.details_visible = true;
            this.toggle_save_button();
            this.$('.client-details:not(.edit) .client-name').off().on('click', function(e){
                self.pos.open_record_in_backend('event.registration', attendee.id);
            });
//            this.show_update_button();
        } else if (visibility === 'edit') {
            // Connect the keyboard to the edited field
            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                contents.off('click', '.detail');
                searchbox.off('click');
                contents.on('click', '.detail', function(ev){
                    self.chrome.widget.keyboard.connect(ev.target);
                    self.chrome.widget.keyboard.show();
                });
                searchbox.on('click', function() {
                    self.chrome.widget.keyboard.connect($(this));
                });
            }

            this.editing_client = true;
            contents.empty();
            contents.append($(QWeb.render('AttendeeDetailsEdit',{widget:this,attendee:attendee})));
            this.toggle_save_button();

            // Browsers attempt to scroll invisible input elements
            // into view (eg. when hidden behind keyboard). They don't
            // seem to take into account that some elements are not
            // scrollable.
            contents.find('input').blur(function() {
                setTimeout(function() {
                    self.$('.window').scrollTop(0);
                }, 0);
            });

            contents.find('.image-uploader').on('change',function(event){
                self.load_image_file(event.target.files[0],function(res){
                    if (res) {
                        contents.find('.client-picture img, .client-picture .fa').remove();
                        contents.find('.client-picture').append("<img src='"+res+"'>");
                        contents.find('.detail.picture').remove();
                        self.uploaded_picture = res;
                    }
                });
            });
        } else if (visibility === 'hide') {
            contents.empty();
            parent.height('100%');
            if( height > scroll ){
                contents.css({height:height+'px'});
                contents.animate({height:0},400,function(){
                    contents.css({height:''});
                });
            }else{
                parent.scrollTop( parent.scrollTop() - height);
            }
            this.details_visible = false;
            this.toggle_save_button();
        }
    },
//    show_update_button: function(){
//        var update_button_html = QWeb.render('AttendeeUpdateButton',{widget: this});
//        var update_button_div = this.$el.find('.attendee-update-buttons');
//        update_button_div.innerHTML = update_button_html;
//
//    },

    close: function(){
        this._super();
        if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
            this.chrome.widget.keyboard.hide();
        }
    },
});
gui.define_screen({name:'attendeelist', widget: AttendeeListScreenWidget});

var AttendeeButton = screens.ActionButtonWidget.extend({
    template: 'AttendeeButton',
    button_click: function () {
        this.gui.show_screen('attendeelist');
    },
});

screens.define_action_button({
    'name': 'attendee_button',
    'widget': AttendeeButton,
    'condition': function(){
        return this.pos.config.pos_event_set_id;
    },
});

gui.Gui.prototype.screen_classes.filter(function(el) {
    return el.name === 'clientlist';
})[0].widget.include({
    display_client_details: function(visibility, partner, clickpos){
        var self = this;
        this._super(visibility, partner, clickpos);
        if(visibility === 'show'){
            this.$('.client-details:not(.edit) .client-name').off().on('click', function(e){
                self.pos.open_record_in_backend('res.partner', partner.id);
            });
        }
    },
});

screens.ReceiptScreenWidget.include({
    show: function(){
        this._super();
        var self = this;
        var attendee_button = this.$el.find('.button.attendee');
        attendee_button.hide();
        this.pos.bind('changed:attendee', function(res){
            if(!res.attendees){
                return;
            }
            var client = this.get_order().get_client();
            var attendee = this.db.attendee_by_id[res.attendees[0]];
            if (client && client.id === attendee.partner_id[0]){
                attendee_button.on('click', function(e){
                    self.click_next();
                    var attendeelist = self.pos.gui.screen_instances.attendeelist;
                    self.pos.gui.show_screen('attendeelist');
                    attendeelist.display_client_details('show',attendee);
                    attendeelist.current_attendee = attendee;
                });
                attendee_button.show();
            }
        });
    },
});

return {
    AttendeeButton: AttendeeButton,
    AttendeeListScreenWidget: AttendeeListScreenWidget,
};

});
