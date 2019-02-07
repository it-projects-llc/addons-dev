odoo.define('web.ListRendererextend', function (require) {
    "use strict";
    var list_view = require('web.ListRenderer');
    var core = require('web.core');
    var _t = core._t;
    var _lt = core._lt;
    var session = require('web.session');
    var field_utils = require('web.field_utils');
    var relational_field = require('web.relational_fields');

    list_view.include({
        _renderBodyCell: function(record, node, colIndex, options){
            var self = this ;
            var field_binary =false;
            var result = self._super(record, node, colIndex, options);
            if(options.mode == 'readonly' && record.res_id && node && node.attrs['name'] == 'image' && record.model == 'megamenu.links'){
                var download_url = session.url('/web/content', {
                    model: 'megamenu.links',
                    field: 'image',
                    id: record.res_id,
                    download: true,
                    filename_field: 'image_name',
                });
                var tdClassName = 'o_data_cell';
                var $td = $('<td>', {'class': tdClassName});
                result = '';
                if(record.data['image'] != false)
                    result = '<a download="' + record.data['name'] + '" href=" ' + download_url+ '">Download</a>';
                return $td.html(result);
            }
            else{
                if(options.mode == 'readonly' && record.res_id && node && node.attrs['name'] == 'image' && record.model == 'megamenu.categories_menu_lines'){
                    var download_url = session.url('/web/content', {
                        model: 'megamenu.categories_menu_lines',
                        field: 'image',
                        id: record.res_id,
                        download: true,
                        filename_field: 'image_name',
                    });
                    var tdClassName = 'o_data_cell';
                    var $td = $('<td>', {'class': tdClassName});
                    result = '';
                    if(record.data['image'] != false)
                        result = '<a download="' + record.data['name'] + '" href=" ' + download_url + '">Download</a>';
                    return $td.html(result);
                }
            }
            return result;
        }
    });
});