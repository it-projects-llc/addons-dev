odoo.define('website_sale.tour', function (require) {
'use strict';

var tour = require("web_tour.tour");
var base = require("web_editor.base");

var options = {
    test: true,
    url: '${start_url}',
    wait_for: ${wait_for},
    % if skip_enabled:
    skip_enabled: true,
    % endif
};

% for set in set_ids:
    // С названием функции надо что то делать, т.к. название может быть не одним словом, не латиницей и т.д
    function ${set.set_name}() { // Надо додумать что делать с аргументами, пока не определился; по идее, сюда должны передаваться аргументы
        return [
            % for step in set.template_id.step_ids:
                // тут должны быть отдельные шаги
                {
                    % if step.content:
                    content: '${step.content}',
                    % endif
                    trigger: '${step.trigger}',
                    % if step.extra_trigger:
                    extra_trigger: '${step.extra_trigger}',
                    % endif
                    % if step.timeout:
                    timeout: ${step.timeout},
                    % endif
                    % if step.position:
                    position: '${step.position}',
                    % endif
                    % if step.width:
                    width: ${step.width},
                    % endif
                    % if step.edition and step.edition != 'both':
                    edition: '${step.edition}',
                    % endif
                    % if step.run:
                    run: '${step.run}',
                    % endif
                    % if step.auto:
                    auto: true,
                    % endif
                },
            % endfor
        ];
    }
% endfor

var = steps = [];

% for set in set_ids:
steps = steps.concat(${set.name}())
% endfor

var tour_name = '${tour_name}';
tour.register(tour_name, options, steps);

});
