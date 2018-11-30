odoo.define('ci_js.tour', function (require) {
'use strict';
    // TODO: think about imports, should it compute which import should be or just should import all of it?

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");
    var core = require('web.core');
    var _t = core._t;

    var options = {
        test: true,
        url: '${start_url}',
        % if wait_for:
        wait_for: ${wait_for},
        % endif
        % if skip_enabled:
        skip_enabled: true,
        % endif
    };

    % for set in set_ids:
    ${set.content_with_args}
    % endfor

    var steps = [];
    % for set in set_ids:
    steps = steps.concat(${set.name}());
    % endfor

    tour.register('${tour_name}', options, steps);
});
