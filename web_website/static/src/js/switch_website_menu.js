// Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
odoo.define('web_website.SwitchWebsiteMenu', function(require) {
"use strict";

var Model = require('web.Model');
var session = require('web.session');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var core = require('web.core');
var _t = core._t;

var SwitchWebsiteMenu = Widget.extend({
    template: 'SwitchWebsiteMenu',
    willStart: function() {
        if (!session.user_websites) {
            return $.Deferred().reject();
        }
        return this._super();
    },
    start: function() {
        var self = this;
        this.$el.on('click', '.dropdown-menu li a[data-menu]', _.debounce(function(ev) {
            ev.preventDefault();
            var website_id = $(ev.currentTarget).data('website-id') || false;  // write method ignores undefinded
            new Model('res.users').call('write', [[session.uid], {'backend_website_id': website_id}]).then(function() {
                location.reload();
            });
        }, 1500, true));

        var all_websites_text =  _t('All Websites');
        var topbar = self.$('.oe_topbar_name');
        var current_website = session.user_websites.current_website;
        if (current_website)
            self.$('.oe_topbar_name').text(current_website[1]);
        else
            self.$('.oe_topbar_name').html('<em>' + all_websites_text + '</em>');

        var websites_list = '';

        var websites = session.user_websites.allowed_websites
        websites.unshift(false);
        _.each(websites, function(website) {
            var a = '';
            if (!website && !current_website || website[0] === session.user_websites.current_website[0]) {
                a = '<i class="fa fa-check o_current_company"></i>';
            } else {
                a = '<span class="o_company"/>';
            }
            if (!website){
                websites_list += '<li><a href="#" class="all_websites" data-menu="website"><em>' + a + all_websites_text + '</em></a></li>';
            } else {
                websites_list += '<li><a href="#" data-menu="website" data-website-id="' + website[0] + '">' + a + website[1] + '</a></li>';
            }
        });
        self.$('.dropdown-menu').html(websites_list);
        return this._super();
    },
});

SystrayMenu.Items.push(SwitchWebsiteMenu);

});
