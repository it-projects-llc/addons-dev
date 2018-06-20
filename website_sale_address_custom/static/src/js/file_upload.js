/* Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */

odoo.define('website_sale_address_custom', function (require) {
    "use strict";

    var Model = require('web.Model');

    $(document).ready(function () {
        if(window.location.href.indexOf("address") > -1) {
            var $input = $('input[type="file"]')[0],
                $selection = $('select[name="identification_id_select"]'),
                $file = $('input[name="identification_file"'),
                reader = new FileReader(),
                data = false,
                res = false;

            reader.onload = function(e){
                res = e.target.result
                data = res.substring(res.indexOf(',') + 1, res.length);
                $file.val(data);
                data = false;
            }

            $input.addEventListener('change', function(ev){
                if($input.files.length){
                    reader.readAsDataURL($input.files[0]);
                }
                if (this.value){
                    $selection.val('');
                }
            });

            $selection.on('change', function(e){
                if (this.value){
                    $input.value = '';
                    $file.val('');
                }
            });
        }
    });
});
