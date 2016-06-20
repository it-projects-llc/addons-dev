odoo.define('web_form_svg.form_widgets', function (require) {
"use strict";

var core = require('web.core');
var common = require('web.form_common');
var data = require('web.data');
var utils = require('web.utils');
var relational = require('web.form_relational');

var FieldSVG = relational.AbstractManyField.extend({
    template: 'FieldSVG',
    init: function(field_manager, node) {
        this._super(field_manager, node);
        if (!this.node.attrs.svg_colors) {
            return;
        }
        this.colors = _(this.node.attrs.svg_colors.split(';')).chain()
            .compact()
            .map(function(color_pair) {
                return color_pair.split(':');
            }).value();
        this.color_field = this.node.attrs.svg_color_field;
        this.id_field = this.node.attrs.svg_id_field;
    },
    get_render_data: function(ids){
        var self = this;
        return this.mutex.exec(function() {
            var fields = [self.id_field, self.color_field];
            return self.dataset.read_ids(ids, fields);
        });
    },
    bind_events: function(data) {
        var self = this;
        _.each(data, function(record){
            var $el = self.$('svg').find('#'+record[self.id_field]);
            $el.off('click');
            $el.on('click', function() {
                if (!self.get("effective_readonly")) {
                    self.change_color($(this));
                }
            });
        });
    },
    color_element: function(data) {
        var self = this;
        _.each(data, function(record){
            var $path = self.$('svg').find('#'+record[self.id_field]);
            self.original_values[record[self.id_field]] = record;
            self.original_colors[record[self.id_field]] = $path.attr('fill');
            _.each(self.colors, function(color) {
                if(color[1] == record[self.color_field]) {
                    if (color[0] != 'original') {
                        $path.attr('fill',color[0]);
                    }
                }
            });
        });
    },
    change_color: function($el) {
        if (!this.colors) {
            return;
        }
        var id = $el.attr('id');
        var old_color = $el.attr('fill');
        if (old_color == this.original_colors[id]) {
            old_color = 'original';
        }
        var new_value;
        var data = {};

        // Current Color = The last color from the list of colors
        if (old_color == this.colors[this.colors.length-1][0]) {
            new_value = this.colors[0][1];
        }
        else {
            for (var i=0; i<this.colors.length; i++) {
                if (old_color == this.colors[i][0]) {
                    new_value = this.colors[i+1][1];
                    break;
                }
            }
        }
        data[this.color_field] = new_value;
        // Update o2m values
        this.data_update(this.original_values[id].id, data);
    },
    render_value: function() {
        var self = this;
        this.original_colors = {};
        this.original_values = {};
        var $svg = this.$('svg');
        $.get(this.node.attrs.svg_file, function(data) {
            $svg.replaceWith(data.documentElement);
            var values = self.get("value");
            var handle_names = function(data) {
                if (self.isDestroyed())
                    return;
                var indexed = {};
                _.each(data, function(el) {
                    indexed[el['id']] = el;
                });
                data = _.map(values, function(el) { return indexed[el]; });
                self.color_element(data);
                self.bind_events(data);
            };
            if (!values || values.length > 0) {
                return self.get_render_data(values).done(handle_names);
            } else {
                handle_names([]);
            }
        });
    },
});

core.form_widget_registry.add('svg', FieldSVG);
return {
    FieldSVG: FieldSVG
};
});