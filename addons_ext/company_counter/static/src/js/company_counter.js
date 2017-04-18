odoo.define('company_counter.management',function(require){
    "use strict";
    var ajax = require("web.ajax");
    $(document).ready(function(){
        var $productDisable = $(".product-inactive");
        $productDisable.on("click",function(ev){
            console.log(ev);
            ev.preventDefault();
            ev.stopPropagation();
            var params = {};
            var target = ev.currentTarget;
            var counter = target.dataset["counter"];
            if (counter){
                params.counter = counter;
            }
            var product = target.dataset["product"];
            if (product){
                params.product = product;
            }
            ajax.jsonRpc("/counter/product/inactive/",'call',params).then(function(data){
                if (data){
                   $(ev.currentTarget.parentNode.parentNode).addClass("hide");
                }
            });
        });
    });
});