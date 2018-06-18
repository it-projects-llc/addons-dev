/* Copyright 2018 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */

odoo.define('website_sale_address_custom', function (require) {
    "use strict";

    var Model = require('web.Model');

//    upload_file = function(e){
//        return new Model('res.partner').call('upload_file', [data]);
//    }
    $(document).ready(function () {
        if(window.location.href.indexOf("address") > -1) {
           alert("your url contains the name franky");
        }
        var input = $('input[type="file"]')[0]
        input.addEventListener('change', function(ev){
            var data = false;
            if(input.files.length){
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]);
                reader.onload = function(e){
                    data = {'file': e.target.result};
                }
            }
            if (data) {
                alert('dasdsa');
            }
        });
    });


});
