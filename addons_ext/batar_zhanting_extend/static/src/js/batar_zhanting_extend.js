openerp.batar_zhanting_extend = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    var page_limit = 14;


    var model = new instance.web.Model("zhanting");
    var userModel = new instance.web.Model("res.users");
    var saleModel = new instance.web.Model('sale.order');

    var confirm_order_button_type = function(type){
        if (type == undefined){
            type = 'none';
        }
        $('.confirm-change').css('display',type);
        $('.cancel-change').css('display',type);

    };
    var update_current_cancel_button=function(self,type){
        if (type == undefined){
            type = 'none';

        }
        $('.cancel-current-page-change').css('display',type);
    };
    //生成我的订单中某一行的table数据
    var gen_one_line_table_context= function(product){
        var trHtml = "";
        var change_flag =0;
        if (product.exchange_qty !=0  || product.change_qty != 0){
            change_flag = 1;
        }
        var virtual_available = product.virtual_available;
        var disabled="disabled";

        if (virtual_available>0){
            disabled = "";
        }

        trHtml += '<tr class="bodyProduct" id="trProduct-'+product.id+'" data-change="'+change_flag+'">'
                +'<td>'
                +'<span>'+product.name+'</span>'
                +'</td>'
                +'<td>'
                +'<span>'+product.default_code+'</span>'
                +'</td>'
                +'<td class="available-qty">'
                +'<span class="'+product.unitClass+'">'+virtual_available+'</span>'
                +'</td>'
                +'<td>'
                +'<span>'+product.real_time_price_unit+'</span>'
                +'</td>'
                +'<td>'
                +'<span>'+product.weight_fee+'</span>'
                +'</td>'
                +'<td>'
                +'<span class="weightClass" >'+product.standard_weight+'</span>'
                +'</td>'
                +'<td >'
                +'<button class="confirm-product-sub btn-sm" >-</button>'
                +'<input type="text"  class="confirm-product-order-qty" data-step="'+product.step+'" value="'+product.order_qty+'"id="confirmProduct-'+product.id+'"/>'
                +'<button class="confirm-product-add btn-sm">+</button>'
                +'</td>';
        if(disabled.length != 0){
            trHtml+='<td >'
                +'<button class="exchange-product-sub btn-sm dis-disabled" disabled="disabled" >-</button>'
                +'<input type="text"  disabled="disabled" class="exchange-product-change-qty dis-disabled" value="'+product.exchange_qty+'"id="changeProduct-'+product.id+'"/>'
                +'<button class="exchange-product-add btn-sm dis-disabled"  disabled="disabled">+</button>'
                +'</td>';
        }else{
            trHtml+='<td >'
                +'<button class="exchange-product-sub btn-sm ">-</button>'
                +'<input type="text"  class="exchange-product-change-qty " data-step="'+product.step+'" value="'+product.exchange_qty+'"id="changeProduct-'+product.id+'"/>'
                +'<button class="exchange-product-add btn-sm"  >+</button>'
                +'</td>';
        }

        trHtml +='<td>'
                +'<span>'+product.total_qty+'</span>'
                +'</td>'
                +'<td>'
                +'<span>'+product.state+'</span>'
                +'</td>'
                +'</tr>';
        return trHtml;
    };

    //更新左侧客户信息，包括当前客户，最近客户
    var update_customer_info = function(self,current_customer,recent_customer_list){
        var currentCustomerNode = self.$el.find(".current-customer")[0];
        var currentCustomerBtnHtml = '';
        if (current_customer != undefined){
            currentCustomerBtnHtml +='<button class="currentCustomer"'+'data-customer-id="'+current_customer.id+'">'
                        +'名称:'+current_customer.name
                        +'<br/>'
                        +'编号:'+current_customer.code
                        +'<br/>'
                        +'电话:'+current_customer.phone
                        +'</button>';
            currentCustomerBtnHtml +='\
                        <div>\
                        	<button class="subStore-btn">门店10</button>\
                        </div>\
                        <div>\
                        	<button class="subStore-btn">门店11</button>\
                        </div>\
                        <div>\
                        	<button class="subStore-btn">门店12</button>\
                        </div>\
                        <div>\
                        	<button class="subStore-btn">门店13</button>\
                        </div>\
                        <div>\
                        	<button class="subStore-btn">门店14</button>\
                        </div>';
            currentCustomerBtnHtml +='\
                        <div>\
                          <button class="Add-Store-btn">添加新门店</button>\
                        </div>';
        }
        currentCustomerNode.innerHTML = currentCustomerBtnHtml;
        var recentCustomerListNode = self.$el.find(".current-customer-list")[0];
        var recentCustomerListHtml = "";
        if (recent_customer_list != undefined){
            for (var i=0;i<recent_customer_list.length;i++){
                recentCustomerListHtml += '<button class="recentCustomer"'+'id="'+recent_customer_list[i].id+'">'
                        +'名称:'+recent_customer_list[i].name
                        +'<br/>'
                        +'编号:'+recent_customer_list[i].code
                        +'<br/>'
                        +'电话:'+recent_customer_list[i].phone
                        +'</button>';
            }
        }
        recentCustomerListNode.innerHTML = recentCustomerListHtml;
    };
    var update_confirm_order_top_info = function(self,total_info){
         var pageRightInfoNode = self.$el.find('.ul-page-right-top')[0];
         var pageRightInfoHtml =  "";
         pageRightInfoHtml += '<li>'
            +'    <p class="top-title" id="my_confirm_order">我的订单</p>'
            +'</li>'
            +'<li>'
            +'    <input type="text" class="search-query product-code-search" id="product-code-search" placeholder="输入产品编码搜索"/>'
            +'</li>'
            +'<li><p>总克重(g)：'+total_info.totalWeight+'</p></li>'
            +'<li><p> 预总估价(元)：'+total_info.totalMoney+'</p></li>'
            +'<li><button class="top-button enter-zhanting">返回购物大厅</button></li>'
            +'<li><button class="top-button enter-draft-order">查看我的托盘</button></li>';
         pageRightInfoNode.innerHTML = pageRightInfoHtml;
    };

    //我的订单表内容生成
    var update_confirm_order_table_tbody = function(products){
        var tbody = "";
        var len = products.length;
        for (var i=0;i<len;i++){
            var product = products[i];
            tbody += gen_one_line_table_context(product);
        }
        return tbody;
    };
    //更新我的新单页面数据
    var update_confirm_order_info = function(tab_location_products,type){
        var pageRightInfoHtml = "";
        var locationTabContentHtml = '';
        if(tab_location_products.length>0){
            pageRightInfoHtml += '<ul id="locationTab" class="nav nav-tabs">';
            locationTabContentHtml += '<div id="locationTabContent" class="tab-content">';
            for(var i=0;i<tab_location_products.length;i++){
                var pageConentHtml = "";
                if (i==0){
                    pageRightInfoHtml += '<li class="active">';
                }else{
                    pageRightInfoHtml += '<li>';
                }
                pageRightInfoHtml  +='<a href="'+tab_location_products[i].location_id_href+'" data-toggle="tab">'
                    +tab_location_products[i].name
                    +'</a>'
                    +'</li>';
                locationTabContentHtml += '<div class="'+tab_location_products[i].tab_location_class+' " id="'+tab_location_products[i].location_id+'">';
                locationTabContentHtml += '<table class="table table-bordered table-hover table-condensed text-center">'
                    +'<thead>'
                    +'<tr>'
                    +'<th>产品名称</th>'
                    +'<th>内部货号</th>'
                    +'<th>可售单位</th>'
                    +'<th>饰品价(元/g)</th>'
                    +'<th>工费(元/g)</th>'
                    +'<th>标准克重(g)</th>'
                    +'<th width="160px">预定单位</th>'
                    +'<th width="160px">换货单位</th>'
                    +'<th>变更后单位</th>'
                    +'<th>当前状态</th>'
                    +'</tr>'
                    +'</thead>'
                    +' <tbody class="table-body">';

                locationTabContentHtml += update_confirm_order_table_tbody(tab_location_products[i].products);
                var page_list = tab_location_products[i].page_list;
                pageConentHtml += '<div>';
                pageConentHtml += gen_page_list_html(page_list, tab_location_products[i].current_page, tab_location_products[i].page_last, tab_location_products[i].location_id,'confirmPageLocation');
                pageConentHtml += '</div>';
                var orderBtnHtml = "";
                //若有变更显示响应的按钮

                orderBtnHtml += '<div class="confirm-order-buttons"><button class="confirm-change" style="display:'
                +tab_location_products[i].show_button+'" >确认所有变更</button>'
                    +'<button class="cancel-change" style="display:'
                    +tab_location_products[i].show_button+'">取消所有变更</button>'
                    +'<button class="cancel-current-page-change" style="display:'+tab_location_products[i].show_button+'">取消当前页变更</button>'
                    +'<button class="cancel-all-order" >取消订单</button></div>';


                locationTabContentHtml += '</tbody></table>';
                locationTabContentHtml += orderBtnHtml;
                locationTabContentHtml += pageConentHtml;
                locationTabContentHtml += '</div>';

            }
            pageRightInfoHtml += ' </ul>';
            locationTabContentHtml += '</div>';
            pageRightInfoHtml += locationTabContentHtml;


        }else{
            pageRightInfoHtml = '<div class="warning-info"><h1>暂无数据,请在<mark>我的托盘</mark>中确认订单或返回<mark>购物大厅</mark>下单</h1></div>';
        }
        return  pageRightInfoHtml;
    };
    var gen_page_list_html = function(page_list,current_page,page_last,location_id,type){
        var pageHtml = "";
        var pageClass = '';

        pageHtml += '<div class="page-content page'+location_id+' '+type+'">';
        if (page_last != undefined){
            if(current_page==1){
                pageClass = ' current-page';
            }
            pageHtml += '<button class="btn-sm'+pageClass+' page page-1" >首页</button>';
        }
        for(var j=0;j<page_list.length;j++){
            if(current_page==page_list[j]){
                pageClass = ' current-page';
            }
            pageHtml +='<button  class="btn-sm'+pageClass+' page page-'+page_list[j]+'">'+page_list[j]+'</button>';
            pageClass = "";
        }
         if (page_last != undefined){
            if(current_page==page_last){
                pageClass = ' current-page';
            }
            pageHtml += '<button class="btn-sm'+pageClass+' page page-'+page_last+'" >尾页</button>';
            pageHtml += '<label for="go-page">跳转</label>';
            pageHtml += '<input type="text" id="go-page" name="goPage" max="'+page_last+'" min="1"/>';
            pageHtml += '<p>共'+page_last+'页</t></p>';
        }
        pageHtml += '</div>';

        return pageHtml;
    };
    var update_page_list_node = function(self,page_list,current_page,page_last,location_id,type){
        var pageNode = self.$el.find('.page-content')[0].parentNode;
        pageNode.innerHTML = gen_page_list_html(page_list,current_page,page_last,location_id,type);
    };
    //更新购物大厅页面顶部信息
    var update_zhanting_top_info= function(self,total_info){
         var pageRightInfoNode = self.$el.find('.ul-page-right-top')[0];
         var pageRightInfoHtml =  "";
         pageRightInfoHtml += '<li>'
            +'    <p class="top-title" id="exhibition_hall">购物大厅</p>'
            +'</li>'
            +'<li>'
            +'    <input type="text" class="search-query product-code-search" id="product-code-search" placeholder="输入产品编码搜索"/>'
            +'</li>'
            +'<li><p>总克重(g)：'+total_info.totalWeight+'</p></li>'
            +'<li><p> 预总估价(元)：'+total_info.totalMoney+'</p></li>'
            +'<li><button class="top-button enter-draft-order">查看我的托盘</button></li>'
            +'<li><button class="top-button enter-confirm-order">查看我的订单</button></li>';

         pageRightInfoNode.innerHTML = pageRightInfoHtml;

    };
     //更新今日客户页面顶部信息
    var update_customer_info_top = function(self){
        var topNode = self.$el.find('.ul-page-right-top')[0];
        var topNodeHtml = "";
        topNodeHtml += '<li><p class="top-title" id="today_customer">今日客户</p> </li>';
        topNodeHtml += '<li><input type="text" class="search-query customer-search" id="customer-search" placeholder="名称/编码/手机号码"/></li>';
        topNodeHtml += '<li><button class="top-button enter-zhanting">返回购物大厅</button></li>';
        topNode.innerHTML = topNodeHtml;
    };
    //我的订单页面顶部信息
    var update_customer_confirm_order_top_info = function(self,total_info){
        var pageRightInfoNode = self.$el.find('.ul-page-right-top')[0];
        var pageRightInfoHtml =  "";
        var total_weight =  total_info.total_weight || 0 ;
        var total_money = total_info.total_money ||0;
        pageRightInfoHtml += '<li>'
            +'    <p class="top-title" id="my_confirm_order" >我的订单</p>'
            +'</li>'
            +'<li>'
            +'    <input type="text" class="search-query product-code-search" id="product-code-search" placeholder="输入产品编码搜索"/>'
            +'</li>'
            +'<li><p>总克重(g)：'+total_weight  +'</p></li>'
            +'<li><p> 预总估价(元)：'+total_money +'</p></li>'
            +'<li><button class="top-button enter-zhanting">返回购物大厅</button></li>'
            +'<li><button class="top-button enter-draft-order">查看我的托盘</button></li>';

        pageRightInfoNode.innerHTML = pageRightInfoHtml;
    };
    //我的托盘页面顶部信息
    var update_customer_draft_order_top_info = function(self,total_info){
         var pageRightInfoNode = self.$el.find('.ul-page-right-top')[0];
         var pageRightInfoHtml =  "";
         pageRightInfoHtml += '<li>'
            +'    <p class="top-title" id="my_draft_order" >我的托盘</p>'
            +'</li>'
            +'<li>'
            +'    <input type="text" class="search-query product-code-search" id="product-code-search" placeholder="输入产品编码搜索"/>'
            +'</li>'
            +'<li><p>总克重(g)：'+total_info.totalWeight +'</p></li>'
            +'<li><p> 预总估价(元)：'+total_info.totalMoney +'</p></li>'
            +'<li><button class="top-button enter-zhanting">返回购物大厅</button></li>'
            +'<li><button class="top-button enter-confirm-order">查看我的订单</button></li>';

         pageRightInfoNode.innerHTML = pageRightInfoHtml;
    };
    var gen_customer_info_page= function(page_list,current_page,page_last){
        var pageHtml = "";
        var pageClass = '';

        pageHtml += '<div class="page-content page">';
        if (page_last != undefined){
            if(current_page==1){
                pageClass = ' current-page';
            }
            pageHtml += '<button class="btn-sm'+pageClass+' page page-1" >首页</button>';
        }
        for(var j=0;j<page_list.length;j++){
            if(current_page==page_list[j]){
                pageClass = ' current-page';
            }
            pageHtml +='<button  class="btn-sm'+pageClass+' page page-'+page_list[j]+'">'+page_list[j]+'</button>';
            pageClass = "";
        }
         if (page_last != undefined){
            if(current_page==page_last){
                pageClass = ' current-page';
            }
            pageHtml += '<button class="btn-sm'+pageClass+' page page-'+page_last+'" >尾页</button>';
            pageHtml += '<label for="go-page">跳转</label>';
            pageHtml += '<input type="text" id="go-page" name="goPage" max="'+page_last+'" min="1"/>';
            pageHtml += '<p>共'+page_last+'页</t></p>';
        }
        pageHtml += '</div>';

        return pageHtml;
    };
    //今日客户页面客户信息，采用table表显示
    var update_customer_info_table= function(self,customer_info_dict){
        var customer_list = customer_info_dict.customer_list;
        var customer_list_len = customer_list.length;
        var pageRightInfoNode = self.$el.find('.pageRightInfo')[0];

        var customerTableInfoHtml = '<table class="table table-bordered table-hover table-condensed text-center">'
            +'<thead>'
            +'    <tr>'
            +'       <th>客户名称</th>'
            +'        <th>下单时间</th>'
            +'        <th>客户编号</th>'
            +'       <th>客户电话</th>'
            +'        </tr>'
            +'</thead>'

            +'<tbody class="table-body">';
        for(var i=0;i<customer_list_len;i++){
            customerTableInfoHtml += '<tr class="customer-table " id="customer-'+customer_list[i].id+'">'
                + '<td><span>'+customer_list[i].name+'</span></td>'
                + '<td><span>'+customer_list[i].order_time+'</span></td>'
                + '<td><span>'+customer_list[i].customer_code+'</span></td>'
                + '<td><span>'+customer_list[i].phone+'</span></td>'
                + '</tr>';
        }
        customerTableInfoHtml += '</tbody></table>';
        customerTableInfoHtml += gen_customer_info_page(customer_info_dict.page_list,customer_info_dict.current_page,customer_info_dict.page_last);
        pageRightInfoNode.innerHTML =  customerTableInfoHtml;
    };
    //我的托盘，购物大厅表内容生成
    var update_table_tbody = function(products){
        var tbody = "";
        if (products){
            var len = products.length;
            for (var i=0;i<len;i++){
                var product = products[i];
                tbody += '<tr>'
                    +'<td>'
                    +'<span>'+product.name+'</span>'
                    +'</td>'
                    +'<td>'
                    +'<span>'+product.default_code+'</span>'
                    +'</td>'
                    +'<td class="available-qty">'
                    +'<span class="'+product.unitClass+'">'+product.virtual_available+'</span>'
                    +'</td>'
                    +'<td>'
                    +'<span>'+product.real_time_price_unit+'</span>'
                    +'</td>'
                    +'<td>'
                    +'<span>'+product.weight_fee+'</span>'
                    +'</td>'
                    +'<td>'
                    +'<span class="weightClass">'+product.standard_weight+'</span>'
                    +'</td>'
                    +'<td >'
                    +'<button class="product-sub btn-sm" >-</button>'
                    +'<input type="text"  class="product-order-qty" data-step="'+product.step+'" value="'+product.order_qty+'"id="'+product.id+'"/>'
                    +'<button class="product-add btn-sm">+</button>'
                    +'</td>'
                    +'</tr>';
            }
        }
        return tbody;
    };
    //更新不同柜台标签下的产品信息，一个业务员可以同时拥有多个柜台的权限，例如展厅经理
    var update_tab_location_products = function(self,tab_location_products,type){

        var pageRightInfoNode = self.$el.find(".pageRightInfo")[0];
        var pageRightInfoHtml = "";
        var locationTabContentHtml = '';
        if(tab_location_products && tab_location_products.length>0){
            pageRightInfoHtml += '<ul id="locationTab" class="nav nav-tabs">';
            locationTabContentHtml += '<div id="locationTabContent" class="tab-content">';
            for(var i=0;i<tab_location_products.length;i++){
                var pageConentHtml = "";
                if (i==0){
                    pageRightInfoHtml += '<li class="active">';
                }else{
                    pageRightInfoHtml += '<li>';
                }
                pageRightInfoHtml  +='<a href="'+tab_location_products[i].location_id_href+'" data-toggle="tab">'
                    +tab_location_products[i].name
                    +'</a>'
                    +'</li>';
                locationTabContentHtml += '<div class="'+tab_location_products[i].tab_location_class+' " id="'+tab_location_products[i].location_id+'">';
                locationTabContentHtml += '<table class="table table-bordered table-hover table-condensed text-center">'
                    +'<thead>'
                    +'<tr>'
                    +'<th>产品名称</th>'
                    +'<th>内部货号</th>'
                    +'<th>可售单位</th>'
                    +'<th>饰品价(元/g)</th>'
                    +'<th>工费(元/g)</th>'
                    +'<th>标准克重(g)</th>'
                    +'<th width="160px">预定单位</th>'
                    +'</tr>'
                    +'</thead>'
                    +' <tbody class="table-body">';

                locationTabContentHtml += update_table_tbody(tab_location_products[i].products);
                var page_list = tab_location_products[i].page_list;
                pageConentHtml += '<div>';
                pageConentHtml += gen_page_list_html(page_list, tab_location_products[i].current_page, tab_location_products[i].page_last, tab_location_products[i].location_id,type);
                pageConentHtml += '</div>';

                //订单确认和取消按钮
                var order_id = tab_location_products[i].order_id;
                var orderBtnHtml = "";
                if (order_id != undefined){
                    orderBtnHtml += '<div class="draft-order-buttons"><button class="confirm-order" id="confirmOrder-'+order_id
                        +'">确认订单</button><button class="cancel-order" id="cancelOrder-'+order_id+'">取消订单</button></div>';

                }
                locationTabContentHtml += '</tbody></table>';
                locationTabContentHtml += pageConentHtml;
                locationTabContentHtml += orderBtnHtml;
                locationTabContentHtml += '</div>';

            }
            pageRightInfoHtml += ' </ul>';
            locationTabContentHtml += '</div>';
            pageRightInfoHtml += locationTabContentHtml;
        }else{
            pageRightInfoHtml = '<div class="warning-info"><h1>暂无数据,请返回<mark>购物大厅</mark>下单</h1></div>';
        }
        pageRightInfoNode.innerHTML = pageRightInfoHtml;

    };

    local.HomePage = instance.Widget.extend({
        events:{
            'change #input-add-customer':'add_customer_change',
            'click .page':'page_click',
            'click #add-customer-btn':'add_customer_dialog',
            //客户搜索
            'change #customer-search':'customer_search',
            'click #confirm-add':"confirm_add",
            'click .recentCustomer':'pressRecentCustomer',
            'click .product-sub':'sub_product_qty',
            'click .product-add':'add_product_qty',
            'change .product-order-qty':'change_product_order_qty',
            'change #product-code-search':'search_by_product_code',
            'click #today-customer-manager':'manage_today_customer',
            'click .enter-zhanting':'enter_zhanting',
            'click .customer-table':"add_current_customer_form_table",
            'click .enter-confirm-order':'enter_confirm_order',
            'click .enter-draft-order':'enter_draft_order',
            'click .confirm-order':'confirm_order',
            'click .cancel-order':'cancel_order',
            'click .tab':'page_tab_click',
            //我的订单界面+-和input改变操作
            'click .confirm-product-sub':'confirm_product_sub',
            'click .confirm-product-add':'confirm_product_add',
            'change .confirm-product-order-qty':'change_confirm_product_order_qty',
            'click .exchange-product-sub':'exchange_product_sub',
            'click .exchange-product-add':'exchange_product_add',
            'change .exchange-product-change-qty':'exchange_product_order_qty',
            //我的订单中4个button事件
            'click .confirm-change':'confirm_change',
            'click .cancel-change':'cancel_all_change',
            'click .cancel-current-page-change':'cancel_current_page_change',
            'click .cancel-all-order':'cancel_all_order',
            'click .subStore-btn':'subStore_btn',
            'change #go-page':'page_click',

        },

        add_customer_dialog:function(e){

            $('#listCustomers')[0].innerHTML="";
            $('#input-add-customer')[0].value = "";
            $('#error-info')[0].innerHTML= "";
            $('#confirm-add').attr('disabled',true);

        },
        customer_search:function(e){
            var self = this;
            var searchKey = e.currentTarget.value;
            model.call('search_customer_dict',[0,page_limit,searchKey],{context: new instance.web.CompoundContext()}).then(function(customer_info_dict){
                update_customer_info_table(self,customer_info_dict);
            });
        },
        confirm_product_sub:function(e){
            var self = this;
            var inputNode = e.currentTarget.nextElementSibling;
            var parentNode = e.currentTarget.parentNode.parentNode;
            var step = inputNode.dataset.step;
            var product_id =parseInt(inputNode.attributes['id'].value.split('-')[1]);
            model.call('change_confirm_order_product_info',[product_id,parseFloat(step),'sub'],{context: new instance.web.CompoundContext()}).then(function(result){
                if (result.code && result.code == 'success'){

                    model.call('get_confirm_total_info',[],{context: new instance.web.CompoundContext()}).then(function(total_info){
                        var trHtml = gen_one_line_table_context(result.info);
                        parentNode.innerHTML = trHtml;
                        update_current_cancel_button(self,result.cancel_current_button);
                        confirm_order_button_type(total_info.show_total_button);

                        update_customer_confirm_order_top_info(self,total_info);


                    });
                }
            });
        },
        confirm_product_add:function(e){
            var self = this;
            var parentNode = e.currentTarget.parentNode.parentNode;
            var inputNode = e.currentTarget.previousElementSibling;
            var step = inputNode.dataset.step;
            var product_id =parseInt(inputNode.attributes['id'].value.split('-')[1]);
            model.call('change_confirm_order_product_info',[product_id,parseFloat(step),'add'],{context: new instance.web.CompoundContext()}).then(function(result){
                if (result.code && result.code == 'success'){

                    model.call('get_confirm_total_info',[],{context: new instance.web.CompoundContext()}).then(function(total_info){
                        var trHtml = gen_one_line_table_context(result.info);

                        parentNode.innerHTML = trHtml;
                        update_current_cancel_button(self,result.cancel_current_button);
                        confirm_order_button_type(total_info.show_total_button);
                        update_customer_confirm_order_top_info(self,total_info);
                    });
                }
            });
        },
        change_confirm_product_order_qty:function(e){
            var self = this;
            var target = e.currentTarget;
            var product_qty = parseFloat(target.value);
            var step = parseFloat(target.dataset.step);
            product_qty = step*(parseInt(product_qty/step));
            var product_id = parseInt(e.currentTarget.attributes['id'].value.split('-')[1]);
            var parentNode = e.currentTarget.parentNode.parentNode;
            model.call('change_confirm_order_product_info',[product_id,product_qty,'change'],{context: new instance.web.CompoundContext()}).then(function(result){
                 if (result.code && result.code == 'success'){
                 model.call('get_confirm_total_info',[],{context: new instance.web.CompoundContext()}).then(function(total_info){
                    var trHtml = gen_one_line_table_context(result.info);
                    parentNode.innerHTML = trHtml;
                    update_current_cancel_button(self,result.cancel_current_button);
                    confirm_order_button_type(total_info.show_total_button);
                    update_customer_confirm_order_top_info(self,total_info);
                 });
                }
            });

        },
        exchange_product_sub:function(e){
            var self = this;
            var inputNode = e.currentTarget.nextElementSibling;
            var parentNode = e.currentTarget.parentNode.parentNode;
            var step = inputNode.dataset.step;

            var product_id =parseInt(inputNode.attributes['id'].value.split('-')[1]);
            model.call('change_return_product_number',[product_id,parseFloat(step),'sub'],{context: new instance.web.CompoundContext()}).then(function(result){
                if (result.code && result.code == 'success'){

                    model.call('get_confirm_total_info',[],{context: new instance.web.CompoundContext()}).then(function(total_info){
                        var trHtml = gen_one_line_table_context(result.info);
                        parentNode.innerHTML = trHtml;
                        update_current_cancel_button(self,result.cancel_current_button);
                        confirm_order_button_type(total_info.show_total_button);
                        update_customer_confirm_order_top_info(self,total_info);
                    });
                }
            });
        },
        exchange_product_add:function(e){
            var self = this;
            var parentNode = e.currentTarget.parentNode.parentNode;
            var inputNode = e.currentTarget.previousElementSibling;
            var step = inputNode.dataset.step;
            var product_id =parseInt(inputNode.attributes['id'].value.split('-')[1]);
            model.call('change_return_product_number',[product_id,parseFloat(step),'add'],{context: new instance.web.CompoundContext()}).then(function(result){
                if (result.code && result.code == 'success'){
                    model.call('get_confirm_total_info',[],{context: new instance.web.CompoundContext()}).then(function(total_info){
                        var trHtml = gen_one_line_table_context(result.info);
                        parentNode.innerHTML = trHtml;
                        update_current_cancel_button(self,result.cancel_current_button);
                        confirm_order_button_type(total_info.show_total_button);
                        update_customer_confirm_order_top_info(self,total_info);
                    });
                }
            });
        },
        exchange_product_order_qty:function(e){
            var self = this;
            var target = e.currentTarget;
            var product_qty = parseFloat(target.value);
            var step = parseFloat(target.dataset.step);
            product_qty = step*(parseInt(product_qty/step));

            var product_id = parseInt(e.currentTarget.attributes['id'].value.split('-')[1]);
            var parentNode = e.currentTarget.parentNode.parentNode;
            model.call('change_return_product_number',[product_id,product_qty,'change'],{context: new instance.web.CompoundContext()}).then(function(result){
                 if (result.code && result.code == 'success'){
                     model.call('get_confirm_total_info',[],{context: new instance.web.CompoundContext()}).then(function(total_info){

                        var trHtml = gen_one_line_table_context(result.info);
                        parentNode.innerHTML = trHtml;

                        update_current_cancel_button(self,result.cancel_current_button);
                        confirm_order_button_type(total_info.show_total_button);
                        update_customer_confirm_order_top_info(self,total_info);
                     });
                }
            });
        },
        cancel_all_order:function(e){
            var self = this;
            if( confirm("删除是不可恢复的，你确认要删除吗？")){
                var locationClassArr = $('.confirmPageLocation')[0].attributes['class'].value.split(" ");
                var location_id = undefined;
                locationClassArr.some(function(el){
                    if(el.indexOf('pagelocation-') ==0){
                    location_id = el.split('-')[1];
                        return el.split('-')[1];
                    }
                });
                model.call('cancel_all_order',[0,page_limit,parseInt(location_id)],{context: new instance.web.CompoundContext()}).then(function(result){
                    if (result ==false){
                        alert("订单取消失败，请联系业务员后台取消");
                    }else if (result =='no_data'){
                        self.$el.find('.pageRightInfo')[0].innerHTML = update_confirm_order_info([],'confirmPageLocation');
                            update_customer_confirm_order_top_info(self,'');
                    }else{
                        model.call('get_confirm_total_info',[],{context: new instance.web.CompoundContext()}).then(function(total_info){
                            self.$el.find('.pageRightInfo')[0].innerHTML = update_confirm_order_info(result,'confirmPageLocation');
                            update_customer_confirm_order_top_info(self,total_info);

                        });
                    }
                });
            }

        },
        cancel_current_page_change:function(e){
            var self = this;
            var tableBodyNode = e.currentTarget.parentNode.previousElementSibling.children[1]
            var trNodeList = $("tr[id^='trProduct-']");
            var productIds = [];
            for(var i=0;i<trNodeList.length;i++){
                productIds.push(parseInt(trNodeList[i].attributes['id'].value.split('-')[1]));
            }

            var page = 1;
            var pageClassArr = $('.current-page')[0] && $('.current-page')[0].attributes['class'].value;
            if (pageClassArr){
                pageClassArr = pageClassArr.split(" ");
                pageClassArr.some(function(el){
                    if(el.indexOf('page-') ==0){
                    page = el.split('-')[1];
                        return el.split('-')[1];
                    }
                });
            }
            page = parseInt(page);
            var locationClassArr = $('.confirmPageLocation')[0].attributes['class'].value.split(" ");
            var location_id = undefined;
            locationClassArr.some(function(el){
                if(el.indexOf('pagelocation-') ==0){
                location_id = el.split('-')[1];
                    return el.split('-')[1];
                }
            });

            location_id = parseInt(location_id);

            model.call('cancel_current_page_change',[page-1,page_limit,location_id,productIds],{context: new instance.web.CompoundContext()}).then(function(result){
                model.call('get_confirm_total_info',[],{context: new instance.web.CompoundContext()}).then(function(total_info){
                    tableBodyNode.innerHTML = update_confirm_order_table_tbody(result.products);
                    confirm_order_button_type(total_info.show_total_button);
                    update_current_cancel_button('inline');
                 });
            });
        },
        cancel_all_change:function(e){
            var self = this;
            var tableBodyNode = e.currentTarget.parentNode.previousElementSibling.children[1]
            var locationClassArr = $('.confirmPageLocation')[0].attributes['class'].value.split(" ");
            var page = 1;
            var pageClassArr = $('.current-page')[0] && $('.current-page')[0].attributes['class'].value;
            if (pageClassArr){
                pageClassArr = pageClassArr.split(" ");
                pageClassArr.some(function(el){
                    if(el.indexOf('page-') ==0){
                    page = el.split('-')[1];
                        return el.split('-')[1];
                    }
                });
            }
            page = parseInt(page);
            var location_id = undefined;
            locationClassArr.some(function(el){
                if(el.indexOf('pagelocation-') ==0){
                location_id = el.split('-')[1];
                    return el.split('-')[1];
                }
            });
            location_id = parseInt(location_id);
            model.call('cancel_all_change',[page-1,page_limit,location_id],{context: new instance.web.CompoundContext()}).then(function(result){
                tableBodyNode.innerHTML = update_confirm_order_table_tbody(result.products);
                confirm_order_button_type(result.show_total_button);
                update_current_cancel_button('none');
            });
        },
        confirm_change:function(e){
            var self = this;
            var locationClassArr = $('.confirmPageLocation')[0].attributes['class'].value.split(" ");
            var location_id = undefined;
            locationClassArr.some(function(el){
                if(el.indexOf('pagelocation-') ==0){
                location_id = el.split('-')[1];
                    return el.split('-')[1];
                }
            });
            location_id = parseInt(location_id);
            var location_id = parseInt(e.currentTarget.parentNode.parentNode.attributes['id'].value.split('-')[1]);
            model.call('confirm_change',[location_id],{context: new instance.web.CompoundContext()}).then(function(result){
                self.enter_confirm_order(e);
            });
        },
        page_tab_click:function(e){
            var self = this ;
            $('.currentPageLocation').removeClass('currentPageLocation');
            var tabHref =e.currentTarget.attributes['href'].value;
            tabHref = tabHref.split("#")[1];
            var findClass = 'page'+tabHref;
            $("."+findClass).addClass('currentPageLocation');

        },
        confirm_order:function(e){
            var self= this;
            var order_id = e.currentTarget.attributes['id'].value;
            order_id = parseInt(order_id.split('-')[1]);
            saleModel.call('action_confirm',[order_id],{context: new instance.web.CompoundContext()}).then(function(result){
                self.enter_draft_order(e);
            });
        },
        cancel_order:function(e){
            var self= this;
            var order_id = e.currentTarget.attributes['id'].value;
            order_id = parseInt(order_id.split('-')[1]);

            saleModel.call('action_cancel',[order_id],{context: new instance.web.CompoundContext()}).then(function(result){
                self.enter_draft_order(e);
            });
        },
        enter_draft_order:function(e){
            var self = this;
            model.call("get_customer_draft_order_info",[0,page_limit,'',''],{context: new instance.web.CompoundContext()}).then(function(result){
                model.call('get_draft_order_total',[],{context: new instance.web.CompoundContext()}).then(function(result){
                update_customer_draft_order_top_info(self,result);
             });
                update_tab_location_products(self,result,'draftPageLocation');
            });
        },
        //进入我的订单界面
        enter_confirm_order:function(e){
            var self = this;

            model.call('get_confirm_order',[0,page_limit,'',''],{context: new instance.web.CompoundContext()}).then(function(result){
                model.call('get_confirm_total_info',[],{context: new instance.web.CompoundContext()}).then(function(total_info){
                    self.$el.find('.pageRightInfo')[0].innerHTML = update_confirm_order_info(result,'confirmPageLocation');
                    update_customer_confirm_order_top_info(self,total_info);
                    for(var i=0;i<result.length;i++){
                        confirm_order_button_type(total_info.show_total_button);
                    }
                });
            });
        },
        //获得当前客户草稿订单的统计数据，当前客户可以为空
        get_tab_locations_draft_order_total:function(self){

             model.call('get_draft_order_total',[],{context: new instance.web.CompoundContext()}).then(function(result){
                update_zhanting_top_info(self,result);
             });
        },
        //在今日客户页面点击客户自动添加到当前客户
        add_current_customer_form_table:function(e){
            var self= this;
            var customer_id = e.currentTarget.attributes['id'].value;
            customer_id = customer_id.split('-')[1];
            model.call('change_current_customer',["",customer_id,page_limit],{context: new instance.web.CompoundContext()}).then(function(result){
                if (result['code'] == 'failed'){
                    alert(result['message']);
                }else{
                    //绘制客户信息和最近客户
                    update_customer_info(self,result.current_customer,result.recent_customer_list);
                    //绘制柜台产品信息
                    update_tab_location_products(self,result.tab_location_products,'currentPageLocation');
                    //绘制购物大厅顶部信息
                    self.get_tab_locations_draft_order_total(self);
                }

            });
        },
        //当前用户（业务员）的界面，登录进入展厅初始页面
        display_current_user_info:function(self,current_user_info){
            var htmlValues = {
                'topTitle':current_user_info.top_title,
                'currentCustomer':current_user_info.current_customer,
                'recentCustomerList':current_user_info.recent_customer_list,
                'tab_location_products':current_user_info.tab_location_products,
            }
            self.$el.append(QWeb.render("BatarHomePageTemplate",htmlValues));

        },
        //展厅启动函数
        start: function(){
			var self = this;
            model.call('get_current_user_info',[0,page_limit],{context: new instance.web.CompoundContext()}).then(function(current_user_info){

                self.display_current_user_info(self,current_user_info);

            });

        },
        //从别的页面进入展厅页面
        enter_zhanting:function(e){

            var self = this;
            self.get_tab_locations_draft_order_total(self);
            model.call('get_current_user_info',[0,page_limit],{context: new instance.web.CompoundContext()}).then(function(current_user_info){

                if(current_user_info.tab_location_products){
                    update_tab_location_products(self,current_user_info.tab_location_products,'currentPageLocation');
                }

            });

        },
        //从别的页面进入今日客户页面
        manage_today_customer:function(e){
            var self = this;
            model.call('get_today_customers',[0,page_limit],{context: new instance.web.CompoundContext()}).then(function(customer_info_dict){
                update_customer_info_top(self);
                update_customer_info_table(self,customer_info_dict);
            });
        },
        //通过产品编码搜索产品
        search_by_product_code:function(e){
            var self = this;
            var searchType =  self.$el.find('.top-title')[0].attributes['id'].value;

            var self = this;
        	var searchKey = e.currentTarget.value.split('-')[0];
        	if (searchKey.length!=0){
        	    searchKey = searchKey.split('/')[0];
                //判断是否为编码
                if(searchKey.match(/[^0-9]+-[^0-9]+\\[^0-9]+/)){
                    alert("请输入正确的产品编码");
                }
        	}
        	//我的托盘搜索
        	if ('my_draft_order'== searchType){
        	    model.call("get_customer_draft_order_info",[0,page_limit,'',searchKey],{context: new instance.web.CompoundContext()}).then(function(result){

                    update_tab_location_products(self,result,'draftPageLocation');
                });
        	}
        	//我的订单搜索
        	else if ('my_confirm_order' == searchType){
                model.call('get_customer_confirm_order_info',[0,page_limit,'',searchKey],{context: new instance.web.CompoundContext()}).then(function(result){
                    model.call('get_confirm_total_info',[],{context: new instance.web.CompoundContext()}).then(function(total_info){
                        self.$el.find('.pageRightInfo')[0].innerHTML = update_confirm_order_info(result,'confirmPageLocation');
                        update_customer_confirm_order_top_info(self,total_info);

                    });
                });
        	}else{
                model.call('get_products_by_code',[searchKey,0,page_limit],{context: new instance.web.CompoundContext()}).then(function(tab_location_products){

                    //绘制柜台产品信息
                    update_tab_location_products(self,tab_location_products,'currentPageLocation');
                });
            }
        },
        //修改产品的数量，包括加减，适用于直接修改input中的数据
        change_product_order_qty:function(e){
            var self = this;
            var target = e.currentTarget;
            var product_qty = parseFloat(target.value);
            var step = parseFloat(target.dataset.step);
            product_qty = step*(parseInt(product_qty/step));
            var product_id = parseInt(e.currentTarget.attributes['id'].value);
            var parentNode = e.currentTarget.parentElement.parentElement;
            var availableNode = parentNode.children[2];
            if (product_qty>=0){
                model.call('change_order_product_info',[product_id,product_qty],{context: new instance.web.CompoundContext()}).then(function(result){
                    if(result.code=='failed'){
                        alert(result.message);
                    }else{
                         availableNode.innerHTML ='<span class="'+result.unitClass+'">'+parseFloat(result.virtual_available)+'</span>';
                        e.currentTarget.value = parseFloat(result.product_qty);
                    }
                    self.get_tab_locations_draft_order_total(self);
                });
            }else{
                alert("请输入大于等于0的数字");
            }
        },
        //减少购买的产品数量
        sub_product_qty:function(e){
            var self = this;

            var parentNode = e.currentTarget.parentElement.parentElement;
            var inputNode = e.currentTarget.nextElementSibling;
            var step = inputNode.dataset.step;

            var product_qty = parseFloat(inputNode.value);
            var availableNode = parentNode.children[2];
            var product_id =parseInt(inputNode.attributes['id'].value);
            if (product_qty-step>=0){
                product_qty -= parseFloat(step);
                model.call('change_order_product_info',[product_id,product_qty],{context: new instance.web.CompoundContext()}).then(function(result){
                    if(result.code=='failed'){
                        alert(result.message);
                    }else{
                        availableNode.innerHTML ='<span class="'+result.unitClass+'">'+parseFloat(result.virtual_available)+'</span>';
                        inputNode.value = product_qty;
                    }
                    self.get_tab_locations_draft_order_total(self);

                });
            }
        },
        //增加购买的产品数量
        add_product_qty:function(e){
            var self = this;

            var inputNode = e.currentTarget.previousElementSibling;
            var parentNode = e.currentTarget.parentElement.parentElement;
            var step = inputNode.dataset.step;
            var product_qty = parseFloat(inputNode.value);
            var availableNode = parentNode.children[2];
            var availableQty = parseFloat(availableNode.innerText);
            product_qty += parseFloat(step);

            if (availableQty >= step){
                var product_id =inputNode.attributes['id'].value;
                product_id = parseInt(product_id);
                model.call('change_order_product_info',[product_id,product_qty],{context: new instance.web.CompoundContext()}).then(function(result){
                    if(result.code=='failed'){
                        alert(result.message);
                    }else{
                        availableNode.innerHTML ='<span class="'+result.unitClass+'">'+parseFloat(result.virtual_available)+'</span>';
                        inputNode.value = product_qty;
                    }
                    self.get_tab_locations_draft_order_total(self);

                });
            }
        },
        
        //点击某个最近客户，切换到当前客户
        pressRecentCustomer:function(e){
            var self = this;
            var customer_id = e.currentTarget.attributes['id'].value;
            customer_id = customer_id.split('-')[1];
            model.call('change_current_customer',["",customer_id,page_limit],{context: new instance.web.CompoundContext()}).then(function(result){
                if (result['code'] == 'failed'){
                    alert(result['message']);
                }else{
                    //绘制客户信息和最近客户
                    update_customer_info(self,result.current_customer,result.recent_customer_list);
                    //绘制柜台产品信息
                    update_tab_location_products(self,result.tab_location_products,'currentPageLocation');
                    //绘制购物大厅顶部
                    self.get_tab_locations_draft_order_total(self);

                }

            });
        },
        //通过弹框添加为当前客户
        confirm_add:function(e){
            var self = this;
            var selectCustomer = self.$el.find('#input-add-customer');
            selectCustomer = selectCustomer && selectCustomer[0] && selectCustomer[0].value;
            if(selectCustomer){
                model.call('change_current_customer',[selectCustomer,"",page_limit],{context: new instance.web.CompoundContext()}).then(function(result){

                    if (result.code == 'failed'){
                        alert(result.message);
                    }else{
                        //绘制客户信息和最近客户
                        update_customer_info(self,result.current_customer,result.recent_customer_list);
                        //绘制柜台产品信息
                        update_tab_location_products(self,result.tab_location_products,'currentPageLocation');
                        self.get_tab_locations_draft_order_total(self);
                        $('#listCustomers')[0].innerHTML="";
                        //使用jquery隐藏模态对话框
                        $('#addCustomerModal').modal('hide');

                    }
                });
            }else{
                alert("信息不完整");
            }
        },
        //页面跳转
        page_click:function(e){

            var self = this;
            //购物大厅，我的托盘，我的订单翻页
           //判断是否为购物大厅，我的托盘，我的订单翻页
            if(self.$el.find('.product-code-search')[0]){
                var searchKey =  self.$el.find('.product-code-search')[0].value;
                var page = 1;
                if (searchKey.length!=0){
                    searchKey = searchKey.split('/')[0];
                    //判断是否为编码
                    if(searchKey.match(/[^0-9]+-[^0-9]+\\[^0-9]+/)){
                        alert("请输入正确的产品编码");
                    }
        	    }
                if (parseInt(e.currentTarget.value)){
                    page = parseInt(e.currentTarget.value);
                }else{
                    var pageClassArr = e.currentTarget.attributes['class'].value;
                    pageClassArr = pageClassArr.split(" ");
                    pageClassArr.some(function(el){
                        if(el.indexOf('page-') ==0){
                        page = el.split('-')[1];
                            return el.split('-')[1];
                        }
                    });
                }

                var parentNode = e.currentTarget.parentNode;
                var parentClassArr = parentNode.attributes['class'].value.split(" ");

                var location_id = undefined;
                parentClassArr.some(function(el){
                    if(el.indexOf('pagelocation-') ==0){
                    location_id = el.split('-')[1];
                        return el.split('-')[1];
                    }
                });
                //(self,page_list,current_page,page_last,location_id,type)

                //判断是否为购物大厅的翻页
                if(parentClassArr.some(function(item){return item == 'currentPageLocation';})){
                    model.call('get_one_page_tab_location',[page-1,page_limit,parseInt(location_id),'',searchKey,true],{context: new instance.web.CompoundContext()}).then(function(result){
                        if (result.products != undefined){
                            var tableNode = self.$el.find('#location-'+location_id)[0];
                            if (tableNode){
                                console.log(result);
                                tableNode = tableNode.children[0].children[1];
                                if (result.products){
                                    tableNode.innerHTML = update_table_tbody(result.products);
                                }
                                update_page_list_node(self,result.page_list,result.current_page,result.page_last,"location-"+location_id,'currentPageLocation');
                            }
                        }
                    });
                }
    //            //我的托盘翻页功能
                else if (parentClassArr.some(function(item){return item == 'draftPageLocation';})){
                    model.call('get_one_page_tab_location_draft_order',[page-1,page_limit,parseInt(location_id),searchKey],{context: new instance.web.CompoundContext()}).then(function(result){
                        if (result.products){
                            var tableNode = self.$el.find('#location-'+location_id)[0];
                            if (tableNode){
                                tableNode = tableNode.children[0].children[1];

                                if (result.products){
                                    tableNode.innerHTML = update_table_tbody(result.products);
                                }
                                update_page_list_node(self,result.page_list,result.current_page,result.page_last,"location-"+location_id,'draftPageLocation');
                            }
                        }
                    });
                }
                //我的订单翻页功能
                else if(parentClassArr.some(function(item){return item == 'confirmPageLocation';})){
                    model.call('get_one_page_tab_location_confirm_order',[page-1,page_limit,parseInt(location_id),searchKey],{context: new instance.web.CompoundContext()}).then(function(result){
                        if (result.products){
                            var tableBodyNode = e.currentTarget.parentNode.parentNode.parentNode.children[0].children[1];
                            var tableNode = self.$el.find('#location-'+location_id)[0];
                            if (tableNode){

                                tableNode = tableNode.children[0].children[1];
                                if (result.products){
                                    tableNode.innerHTML = update_confirm_order_table_tbody(result.products);
                                }
                                update_page_list_node(self,result.page_list,result.current_page,result.page_last,"location-"+location_id,'confirmPageLocation');
                            }
                        }


                    });
                }
            }else if (self.$el.find(".customer-search")){
                var searchKey =  self.$el.find('.customer-search')[0].value;
                var page = 1;
                if (parseInt(e.currentTarget.value)){
                    page = parseInt(e.currentTarget.value);
                }else{
                    var pageClassArr = e.currentTarget.attributes['class'].value;

                    pageClassArr = pageClassArr.split(" ");
                    pageClassArr.some(function(el){
                        if(el.indexOf('page-') ==0){
                        page = el.split('-')[1];
                            return el.split('-')[1];
                        }
                    });
                }
                if(page=parseInt(page)){
                    model.call('search_customer_dict',[page-1,page_limit,searchKey],{context: new instance.web.CompoundContext()}).then(function(customer_info_dict){
                        update_customer_info_table(self,customer_info_dict);
                    });
                 }

            }
            $('.current-page').removeClass('current-page');
            $('.page-'+page).addClass('current-page');


        },
        //弹框添加客户输入项改变后请求函数
        add_customer_change:function(e){
            var self = this;
            $('#error-info')[0].innerHTML= "";
            customerInfo = e.currentTarget.value;
            customerInfo = customerInfo.trim();
            if (customerInfo.length != 0){
                model.call('search_customer',[customerInfo],{context: new instance.web.CompoundContext()}).then(function(customerList){
                    if(customerList.length !=0){
                        var listCustomers = self.$el.find("#listCustomers");
                        listCustomers.innerHTML ="";
                        var nodeHtml = "";
                        listCustomers = listCustomers && listCustomers[0];
                        for (var i=0;i<customerList.length;i++){
                            nodeHtml += '<option value="'+customerList[i].name+'" data-id="'+customerList[i].id+'">'+customerList[i].name+'</option>';
                        }
                        $('#confirm-add').attr('disabled',false);
                        listCustomers.innerHTML = nodeHtml;

                    }else{

                        $('#error-info')[0].innerHTML= "系统无相关客户信息，请确认！";
                     }
                });
            }
        },
        subStore_btn:function(e){
          $(".subStore-btn").each(function(i,elem){
            $(elem).css('background-color','#fff');
          });
          $(e.currentTarget).css('background-color','#e0e0e0');
        },
    });
    instance.web.client_actions.add('batar_zhanting_extend.page', 'instance.batar_zhanting_extend.HomePage');
}
