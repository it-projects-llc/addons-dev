odoo.define('mail_private.ChatterComposer', function (require) {
    "use strict";

    var core = require('web.core');
    var form_common = require('web.form_common');
    var composer = require('mail.composer');
    var thread = require('mail.ChatThread');

    var _t = core._t;

    thread.include({
        get_recipients_for_internal_message: function(ids, context){
            var self = this;
            self.result = {};
            return new instance.web.Model(context.default_model).call(
                'read', [ids, ['message_follower_ids'], context]
            ).then(function (thread) {
                for (var i = 0; i < thread.length; i++) {
                    var res_id = thread[i].id;
                    var followers = thread[i].message_follower_ids;
                    self.result[res_id] = [];
                    return new instance.web.Model('res.partner').call(
                        'read', [followers, ['name', 'email', 'user_ids']]
                    ).then(function (res_partners){
                        for (var j = 0; j < res_partners.length; j++) {
                            if (!_.include(res_partners[j].user_ids, self.session.uid)){
                                var partner = res_partners[j];
                                self.result[res_id].push(
                                    [partner.id, partner.name + '<' + partner.email + '>']
                                );
                            }
                        }
                        return self.result;
                    });
                }
                return self.result;
            });
        }
    });

    var ChatterComposer = composer.BasicComposer.extend({
        template: 'mail.chatter.ChatComposer',

        init: function (parent, dataset, options) {
            this._super(parent, options);
            this.parent = parent;
            this.thread_dataset = dataset;
            this.suggested_partners = [];
            this.options = _.defaults(this.options, {
                display_mode: 'textarea',
                record_name: false,
                is_log: false,
                is_internal: false,
                internal_subtypes: []
            });
            if (this.options.is_log) {
                this.options.send_text = _t('Log');
            }
            if (this.options.is_internal) {
                this.options.send_text = _t('Internal');
            }
            this.events = _.extend(this.events, {
                'click .o_composer_button_full_composer': 'on_open_full_composer'
            });
        },

        willStart: function () {
            if (this.options.is_log) {
                return this._super.apply(this, arguments);
            }
            return $.when(this._super.apply(this, arguments), this.message_get_suggested_recipients());
        },

        should_send: function () {
            return false;
        },

        preprocess_message: function () {
            var self = this;
            var def = $.Deferred();
            this._super().then(function (message) {
                message = _.extend(message, {
                    subtype_id: false,
                    subtype: 'mail.mt_comment',
                    message_type: 'comment',
                    content_subtype: 'html',
                    context: self.context
                });

                // Subtype
                if (self.options.is_log) {
                    var subtype_id = parseInt(self.$('.o_chatter_composer_subtype_select').val());
                    if (_.indexOf(_.pluck(self.options.internal_subtypes, 'id'), subtype_id) === -1) {
                        message.subtype = 'mail.mt_note';
                    } else {
                        message.subtype_id = subtype_id;
                    }
                }
                if (self.options.is_internal){
                    message.subtype = false;
                }

                // Partner_ids
                if (!self.options.is_log) {
                    var checked_suggested_partners = self.get_checked_suggested_partners();
                    self.check_suggested_partners(checked_suggested_partners).done(function (partner_ids) {
                        message.partner_ids = (message.partner_ids || []).concat(partner_ids);
                        // update context
                        message.context = _.defaults({}, message.context, {
                            mail_post_autofollow: true
                        });
                        def.resolve(message);
                    });
                } else {
                    def.resolve(message);
                }

            });

            return def;
        },

        /**
        * Send the message on SHIFT+ENTER, but go to new line on ENTER
        */
        prevent_send: function (event) {
            return !event.shiftKey;
        },

        message_get_suggested_recipients: function () {
            var self = this;
            var email_addresses = _.pluck(this.suggested_partners, 'email_address');
            var get_recipients;
            if (this.options.is_internal){
                // todo: не работает вызов метода
                get_recipients = this.parent.thread.get_recipients_for_internal_message([this.context.default_res_id], this.context);
            } else {
                get_recipients = this.thread_dataset.call('message_get_suggested_recipients', [[this.context.default_res_id], this.context]);
            }
            return get_recipients.done(function (suggested_recipients) {
                var thread_recipients = suggested_recipients[self.context.default_res_id];
                _.each(thread_recipients, function (recipient) {
                    var parsed_email = parse_email(recipient[1]);
                    if (_.indexOf(email_addresses, parsed_email[1]) === -1) {
                        self.suggested_partners.push({
                            checked: true,
                            partner_id: recipient[0],
                            full_name: recipient[1],
                            name: parsed_email[0],
                            email_address: parsed_email[1],
                            reason: recipient[2]
                        });
                    }
                });
            });
        },

        /**
         * Get the list of selected suggested partners
         * @returns Array() : list of 'recipient' selected partners (may not be created in db)
         **/
        get_checked_suggested_partners: function () {
            var self = this;
            var checked_partners = [];
            this.$('.o_composer_suggested_partners input:checked').each(function() {
                var full_name = $(this).data('fullname');
                checked_partners = checked_partners.concat(_.filter(self.suggested_partners, function(item) {
                    return full_name === item.full_name;
                }));
            });
            return checked_partners;
        },

        /**
         * Check the additionnal partners (not necessary registered partners), and open a popup form view
         * for the ones who informations is missing.
         * @returns Deferred resolved with the list of checked suggested partners (real partner)
         * @param checked_suggested_partners
         **/
        check_suggested_partners: function (checked_suggested_partners) {
            var self = this;
            var check_done = $.Deferred();

            var recipients = _.filter(checked_suggested_partners, function (recipient) { return recipient.checked; });
            var recipients_to_find = _.filter(recipients, function (recipient) { return (! recipient.partner_id); });
            var names_to_find = _.pluck(recipients_to_find, 'full_name');
            var recipients_to_check = _.filter(recipients, function (recipient) { return (recipient.partner_id && ! recipient.email_address); });
            var recipient_ids = _.pluck(_.filter(recipients, function (recipient) { return recipient.partner_id && recipient.email_address; }), 'partner_id');

            var names_to_remove = [];
            var recipient_ids_to_remove = [];

            // have unknown names -> call message_get_partner_info_from_emails to try to find partner_id
            var find_done = $.Deferred();
            if (names_to_find.length > 0) {
                find_done = self.thread_dataset.call('message_partner_info_from_emails', [[this.context.default_res_id], names_to_find]);
            } else {
                find_done.resolve([]);
            }

            // for unknown names + incomplete partners -> open popup - cancel = remove from recipients
            $.when(find_done).pipe(function (result) {
                var emails_deferred = [];
                var recipient_popups = result.concat(recipients_to_check);

                _.each(recipient_popups, function (partner_info) {
                    var deferred = $.Deferred();
                    emails_deferred.push(deferred);

                    var partner_name = partner_info.full_name;
                    var partner_id = partner_info.partner_id;
                    var parsed_email = parse_email(partner_name);

                    var dialog = new form_common.FormViewDialog(self, {
                        res_model: 'res.partner',
                        res_id: partner_id,
                        context: {
                            force_email: true,
                            ref: "compound_context",
                            default_name: parsed_email[0],
                            default_email: parsed_email[1]
                        },
                        title: _t("Please complete partner's informations"),
                        disable_multiple_selection: true
                    }).open();
                    dialog.on('closed', self, function () {
                        deferred.resolve();
                    });
                    dialog.view_form.on('on_button_cancel', self, function () {
                        names_to_remove.push(partner_name);
                        if (partner_id) {
                            recipient_ids_to_remove.push(partner_id);
                        }
                    });
                });
                $.when.apply($, emails_deferred).then(function () {
                    var new_names_to_find = _.difference(names_to_find, names_to_remove);
                    find_done = $.Deferred();
                    if (new_names_to_find.length > 0) {
                        find_done = self.thread_dataset.call('message_partner_info_from_emails', [[self.context.default_res_id], new_names_to_find, true]);
                    } else {
                        find_done.resolve([]);
                    }
                    $.when(find_done).pipe(function (result) {
                        var recipient_popups = result.concat(recipients_to_check);
                        _.each(recipient_popups, function (partner_info) {
                            if (partner_info.partner_id && _.indexOf(partner_info.partner_id, recipient_ids_to_remove) === -1) {
                                recipient_ids.push(partner_info.partner_id);
                            }
                        });
                    }).pipe(function () {
                        check_done.resolve(recipient_ids);
                    });
                });
            });
            return check_done;
        },

        on_open_full_composer: function() {
            if (!this.do_check_attachment_upload()){
                return false;
            }

            var self = this;
            var recipient_done = $.Deferred();
            if (this.options.is_log) {
                recipient_done.resolve([]);
            } else {
                var checked_suggested_partners = this.get_checked_suggested_partners();
                recipient_done = this.check_suggested_partners(checked_suggested_partners);
            }
            recipient_done.then(function (partner_ids) {
                var context = {
                    default_parent_id: self.id,
                    default_body: get_text2html(self.$input.val()),
                    default_attachment_ids: _.pluck(self.get('attachment_ids'), 'id'),
                    default_partner_ids: partner_ids,
                    default_is_log: self.options.is_log,
                    default_is_internal: self.options.is_internal,
                    mail_post_autofollow: true
                };

                if (self.context.default_model && self.context.default_res_id) {
                    context.default_model = self.context.default_model;
                    context.default_res_id = self.context.default_res_id;
                }

                self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'mail.compose.message',
                    view_mode: 'form',
                    view_type: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    context: context
                }, {
                    on_close: function() {
                        self.trigger('need_refresh');
                        var parent = self.getParent();
                        chat_manager.get_messages({model: parent.model, res_id: parent.res_id});
                    }
                }).then(self.trigger.bind(self, 'close_composer'));
            });
        }
    });

    return ChatterComposer;

});
