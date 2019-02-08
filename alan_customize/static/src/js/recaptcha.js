odoo.define('alan_customize.recaptcha', function (require) {
    "use strict";

    require('web.dom_ready');
    var core = require('web.core');
    var qweb = core.qweb.add_template('/alan_customize/static/src/xml/recaptcha.xml');
    var snippet_animation = require('website.content.snippets.animation');

    snippet_animation.registry.form_builder_send.include({
        send: function (e) {
            e.preventDefault();
            if (!this.check_error_fields([])) {
                this.update_status('invalid');
                return false;
            }
            if(grecaptcha && $('.g-recaptcha').length > 0) {
                if(!grecaptcha.getResponse()) {
                    this.update_status('recaptcha');
                    return false;
                }
            }
            return this._super(e);
        },
    });
});
