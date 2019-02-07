odoo.define('website.theme_custom', function (require) {
'use strict';

var Theme = require('website.theme');
var ColorpickerDialog = require('web.colorpicker');

Theme.include({
    xmlDependencies: (Theme.prototype.xmlDependencies || [])
        .concat(['/theme_alan/static/src/xml/website_editor.xml']),
    events: {
        'change [data-xmlid], [data-enable], [data-disable]': '_onChange',
        'click .checked [data-xmlid], .checked [data-enable], .checked [data-disable]': '_onChange',
        'click .o_theme_customize_color': '_onColorClick',
    },
    _onColorClick: function (ev) {

        var self = this;
        var $color = $(ev.currentTarget);
        var colorName = $color.data('color');
        var colorType = $color.data('colorType');

        var colorpicker = new ColorpickerDialog(this, {
            defaultColor: $color.find('.o_color_preview').css('background-color'),
        });
        colorpicker.on('colorpicker:saved', this, function (ev) {
            ev.stopPropagation();
            // TODO improve to be more efficient
            self._rpc({
                route: '/web_editor/get_assets_editor_resources',
                params: {
                    key: 'website.layout',
                    get_views: false,
                    get_scss: true,
                    bundles: false,
                    bundles_restriction: [],
                },
            }).then(function (data) {
                var files = data.scss[0][1];
                var file = _.find(files, function (file) {
                    var baseURL = '/website/static/src/scss/options/colors/';
                    return file.url === _.str.sprintf('%suser_%scolor_palette.scss', baseURL, (colorType ? (colorType + '_') : ''));
                });
                var colors = {};
                colors[colorName] = ev.data.cssColor;
                if (colorName === 'alpha') {
                    colors['beta'] = 'null';
                    colors['gamma'] = 'null';
                    colors['delta'] = 'null';
                    colors['epsilon'] = 'null';
                }
                var updatedFileContent = file.arch;                
                _.each(colors, function (colorValue, colorName) {
                if(colorName === 'alan'){
		            var updatedFileContent = "$as-theme:\t\t\t\t" + colorValue + ";";
		            var baseURL = '/static/src/scss/options/colors/color_picker.scss';                                
                    $.get("/update_scss_file", {
                        'file_path': baseURL, 'write_str': updatedFileContent
                    });
		            }
		       else{
                    var pattern = _.str.sprintf("'%s': %%s,\n", colorName);
                    var regex = new RegExp(_.str.sprintf(pattern, ".+"));
                    var replacement = _.str.sprintf(pattern, colorValue);
                    if (regex.test(updatedFileContent)) {
                        updatedFileContent = updatedFileContent
                            .replace(regex, replacement);
                    } else {
                        updatedFileContent = updatedFileContent
                            .replace(/( *)(.*hook.*)/, _.str.sprintf('$1%s$1$2', replacement));
                    }		       
		       } 
                })
            }).then(function () {
                self.$('#' + $color.closest('.o_theme_customize_color_previews').data('depends')).click();
            });
        });
        colorpicker.open();
    },
});

});
