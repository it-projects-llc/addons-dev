odoo.define('alan_customize.clean', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    $(document).ready(function(){
        $("body").on('click','.remove_cart',function (ev){
            ev.preventDefault();
            ajax.jsonRpc("/shop/cart/clean_cart", 'call', {}).then(function(data){
                location.reload();
                return;
            });
        return false;
        });
    });
});
