odoo.define('web_widget_heatmap.widget', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var registry = require('web.field_registry');


    var HeatMapWidget = AbstractField.extend({
        fieldsToFetch: {
            display_name: {type: 'char'},
            create_date: {type: 'datetime'},
        },
        template: 'HeatMapWidget',
        supportedFieldTypes: ['one2many', 'many2many'],
        description: "",
        cssLibs: [
            '/web/static/lib/nvd3/nv.d3.css',
            '/web_widget_heatmap/static/lib/css/cal-heatmap.css'
        ],
        jsLibs: [
            '/web/static/lib/nvd3/d3.v3.js',
            '/web/static/lib/nvd3/nv.d3.js',
            '/web/static/src/js/libs/nvd3.js',
            '/web_widget_heatmap/static/lib/js/cal-heatmap.js'
        ],
        get_max_date: function(options) {
            if (options) {
                var max_date = new Date(options.start_date);
                var range = this.nodeOptions ? this.nodeOptions.range : options.range;
                var domain = this.nodeOptions ? this.nodeOptions.domain : options.domain;
                if (domain === 'hour') {
                    max_date.setHours(max_date.getHours() + range);
                } else if (domain === 'day') {
                    max_date.setDate(max_date.getDate() + range);
                } else if (domain === 'week') {
                    max_date.setDate(max_date.getDate() + (range * 7));
                } else if (domain === 'month') {
                    max_date.setMonth(max_date.getMonth() + range);
                } else if (domain === 'year') {
                    max_date.setFullYear(max_date.getFullYear() + range);
                }
                if (max_date > options.end_date) {
                    return max_date;
                }
                return options.end_date;
            }
            return false;
        },
        generate_element_options: function(elements) {
            var start_date = elements.length ? elements[0].create_date.toDate() : new Date();
            var timestamps = elements.map(function(el) {
                return el.create_date.unix();
            });
            var domain = "day";
            var range = 16;
            var end_date = elements.length ? elements[elements.length - 1].create_date.toDate() : null;
            var max_date = this.get_max_date({
                start_date: start_date,
                end_date: end_date,
                domain: domain,
                range: range
            });
            var controls = false;
            if (max_date < end_date) {
                controls = true;
            }
            return {
                start: start_date,
                data: _.chain(timestamps).countBy().value(),
                dataType: 'json',
                minDate: start_date,
                maxDate: max_date,
                controls: controls,
                range: range,
                domain: domain,
                subDomain: "hour",
                domainGutter: 0,
                highlight: "now",
                onClick: this.onClickHeatMap.bind(this),
                label: {
                    position: "top"
                }
            };
        },
        _render: function () {
            var elements = this.value ? _.pluck(this.value.data, 'data') : [];
            var options = this.generate_element_options(elements);
            this.controls = options.controls;
            this.renderElement();
            var nodeOptions = this.nodeOptions || {};
            this.heatmap_options = _.extend(nodeOptions, options, {itemSelector: this.$el.find('.o_field_heatmap')[0]});
            this.heatmap = new CalHeatMap();
            this.heatmap.init(this.heatmap_options);
        },
        renderElement: function() {
            this._super();
            this.$el.find('.next').click(this.nextHeatMap.bind(this));
            this.$el.find('.previous').click(this.previousHeatMap.bind(this));
        },
        nextHeatMap: function() {
            this.heatmap.next();
        },
        previousHeatMap: function() {
            this.heatmap.previous();
        },
        onClickHeatMap: function(date, items_count) {
            date = moment(date);
            var options = this.heatmap_options;
            var elements = this.value ? _.pluck(this.value.data, 'data') : [];
            if (elements && elements.length) {
                // TODO: make faster
                var current_elements_ids = elements.filter(function(el) {
                    var duration = moment.duration(date.diff(el.create_date));
                    if (options.domain === 'hour') {
                        return duration.years() === 0 && duration.months() === 0 && duration.weeks() === 0 && duration.days() === 0 && duration.hours() === 0;
                    } else if (options.domain === 'day') {
                        return duration.years() === 0 && duration.months() === 0 && duration.weeks() === 0 && duration.days() === 0;
                    } else if (options.domain === 'week') {
                        return duration.years() === 0 && duration.months() === 0 && duration.weeks() === 0;
                    } else if (options.domain === 'month') {
                        return duration.years() === 0 && duration.months() === 0;
                    } else if (options.domain === 'year') {
                        return duration.years() === 0;
                    }
                    return false;
                }).map(function(el) {
                    return el.id;
                });
                var action = {
                    name: date.format('YYYY-MM-DD HH:mm'),
                    type: 'ir.actions.act_window',
                    res_model: this.value.model,
                    view_mode: 'list,form',
                    views: [[false, 'list'], [false, 'form']],
                    view_type: 'list',
                    domain: [['id', 'in', current_elements_ids]],
                };
                return this.do_action(action);
            }
        },
    });

    registry.add('heatmap', HeatMapWidget);

    return HeatMapWidget;
});
