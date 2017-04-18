openerp.out_picking_quality = function(instance,local){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var qualityModel = new instance.web.Model("out.picking.quality");
    var wigthObj = null;
    var reasonOption = '';
    var Reg = /^\d+(\.\d+)?(\s+)?$/　;

    var tcommUtil = {
        tcom : null,
        tcomOpen : false,
        CUR_SJT : 'HEX', // 当前编码 格式 HEX
        COMLI : 3, // 串口号
        SBTL : '9600', // 波特率
        SJYW : 'N', // 校验位 N:None,O:Odd,E:Even,M:Mark,S:Space
        STZW : '1', // 停止位 1、2
        SSJW : '8', // 数据位5\6\7\8
        SSJT : 'HEX', // 编码 格式 HEX、utf-8、Unicode
        init:function(){
            tcommUtil.tcom = tcommUtil.getobj();
        },
        getobj:function(){
            var obj = document.getElementById("tcom_OB");
            try {
                obj.Register("");
                return obj;
            } catch (e) {
                return document.getElementById("tcom_EM");
            }
        },
        closeCom : function() {
            tcommUtil.tcom.CloseCom(); // 关闭串口
            tcommUtil.tcomOpen = false;
            console.log('关闭串口');
        },
        openComPort:function(){
            try{
                tcommUtil.tcom.CloseCom(); // 关闭串口
                tcommUtil.tcomOpen = false;
            }catch(e){}
            try{
                if(tcommUtil.tcomOpen)
                {
                    return true;
                }
                var comSet = tcommUtil.SBTL + "," + tcommUtil.SJYW + ","
					+ tcommUtil.SSJW + "," + tcommUtil.STZW;
                tcommUtil.tcom.DataType = tcommUtil.SSJT;
                console.log("串口参数");
                console.log(tcommUtil.COMLI);
                console.log(tcommUtil.tcom.InitCom(tcommUtil.COMLI, comSet));
                if (tcommUtil.COMLI > 0
                        && tcommUtil.tcom.InitCom(tcommUtil.COMLI, comSet)) { // 打开串口&&
                                                                                // tcom.InitCom(comNo,comSet)
                    tcommUtil.autoRead();
                    tcommUtil.tcomOpen = true;
                    console.log('开启串口');
                    return true;
                }

            }catch(e){
                alert("您还没有安装串口插件，请联系管理员安装");
            }
        },
        autoRead : function() {
            tcommUtil.tcom.onDataIn = function(dat) { // 接收串口返回数据
                console.log('获取：' + dat);
                if (tcommUtil.tcom.DataType == "hex") {

                    var kgCount = tcommUtil.hexCharCodeToStr(dat);
                     console.log(kgCount);
                    if(!kgCount) kgCount = 0;
                    if(wigthObj!=null){
                        var weight =  parseFloat(kgCount).toFixed(2);
                        console.log(weight);
                        wigthObj.currentTarget.value =weight;
                    }else{
                        alert("请选择正确的重量输入框");
                    }

                }
                return true;
            }
        },
        hexCharCodeToStr : function(hexCharCodeStr) {
            var trimedStr = hexCharCodeStr.trim();
            var rawStr = trimedStr.substr(0, 2).toLowerCase() === "0x" ? trimedStr
                    .substr(2) : trimedStr;
            var len = rawStr.length;
            if (len % 2 !== 0) {
                alert("无效 ASCII 编码!");
                return "";
            }
            var curCharCode;
            var resultStr = [];
            for (var i = 0; i < len; i = i + 2) {
                curCharCode = parseInt(rawStr.substr(i, 2), 16); // ASCII Code
                                                                    // Value
                resultStr.push(String.fromCharCode(curCharCode));
            }
            return resultStr.join("");
        },
    };
    var clear_main_info = function(){
        $("#main-info").empty();
    };
    var clear_main_info_action = function(){
        $("#main-info-action").empty();
    };
    var clear_waring_info= function(){
        $("#waring-info").empty();
    };
    var gen_waring_info = function(message){

        var waringNode = $("#waring-info");
        if (waringNode.length>0){
            waringNode[0].innerHTML = "<p>"+message+"</p>";
        }

    };
    var gen_top_title_info = function(){
         var top = $("#main-page-right-top");
        if (top.length>0){
            top[0].innerHTML = '<h1 class="text-center text-primary">等待质检</h1>';
        }
    };
    var gen_main_info_action = function(){
        var infoActionNode = $("#main-info-action");
        if (infoActionNode.length>0){
            infoActionNode[0].innerHTML = '<button class="btn btn-primary customer-quality-check-button" id="customer-quality-check-button" type="button">确定</button>'
        }
    };
    var gen_check_order_search_html = function(){
        var htmlNode = $("#main-page-right-top");
        if (htmlNode.length>0){
            htmlNode = htmlNode[0];
            var qualityCheckHTML = '<div class="text-center">';
            qualityCheckHTML+= '<h1 class="weigh-title">客户质检</h1>';
            qualityCheckHTML += '<label for="check-order-search">请输入包号:</label>';
            qualityCheckHTML += '<input id="check-order-search" class="package-number">';
            qualityCheckHTML += '</div>';
            htmlNode.innerHTML = qualityCheckHTML;
        }
    };
    var display_search_wait_check_order =function(data){

        var dataLen = data.length;
        if (dataLen>0){
            var htmlTable = '<table class="table table-bordered table-hover table-condensed table-striped">';
            htmlTable += '<thead><tr class="info text-center">';
            htmlTable += '<th>客户</th>';
            htmlTable += '<th>单号</th>';
            htmlTable += '<th>分拣员</th>';
            htmlTable += '</tr></thead>';

            htmlTable += '<tbody>';
            for(var i=0;i<dataLen;i++){
                htmlTable += '<tr class="customer-order-wait-check text-center" id="order-'+data[i].id+'"> ';
                htmlTable += '<td>' +data[i].customer+'</td>';
                htmlTable += '<td>' +data[i].name+'</td>';
                htmlTable += '<td>' +data[i].pick_user+'</td>';
                htmlTable += '</tr>';
            }
            htmlTable += '</tbody>';
            htmlTable += '</table>';
            $("#main-info")[0].innerHTML = htmlTable;
        }else{
            $("#main-info")[0].innerHTML = '<p class="text-center text-danger">暂无待验信息</p>';
        }
    };
    var clear_main_info = function(){
       var mainNode =  $("#main-info");
        if (mainNode.length>0){
            mainNode[0].innerHTML = "";
        }
    };
    var list_quality_check_order_line = function(data){

        var htmlNode = $('#main-info');
        if (htmlNode.length>0){
            htmlNode = htmlNode[0];
            var htmlTable = '<table class="table table-bordered table-hover table-condensed table-striped">';
            htmlTable += '<thead><tr class="info text-center">';
            htmlTable += '<th>客户</th>';
            htmlTable += '<th>包号</th>';
            htmlTable += '<th>内部货号</th>';
            htmlTable += '<th>产品名称</th>';

            htmlTable += '<th>毛重</th>';
            htmlTable += '<th>净重</th>';
            htmlTable += '<th>数量/重量</th>';
            htmlTable += '<th>质检数量/重量</th>';
            htmlTable += '<th>退货数量/重量</th>';
            htmlTable += '<th>换货数量/重量</th>';
            htmlTable += '<th>状态</th>';
            htmlTable += '</tr></thead>';
            htmlTable += '<tbody>';
            for(var i=0;i<data.length;i++){
                htmlTable += '<tr class="text-center">';
                htmlTable += '<td>'+data[i].partner+'</td>';
                htmlTable += '<td>'+data[i].name+'</td>';
                htmlTable += '<td>'+data[i].product_code+'</td>';
                htmlTable += '<td>'+data[i].product+'</td>';
                htmlTable += '<td>'+data[i].weight+'</td>';
                htmlTable += '<td>'+data[i].net_weight+'</td>';
                htmlTable += '<td>'+data[i].check_weight+'</td>';
                htmlTable += '<td>'+data[i].qty+'</td>';
                htmlTable += '<td>'+data[i].back_qty+'</td>';
                htmlTable += '<td>'+data[i].exchange_qty+'</td>';
                htmlTable += '<td>'+data[i].state+'</td>';

                htmlTable += '</tr>';
            }
            htmlTable += '</tbody>';
            htmlTable += '</table>';
            htmlNode.innerHTML = htmlTable;
        }
    }
    var gen_quality_check_table = function(data){
        var htmlNode = $('#main-info');
        if (htmlNode.length>0){
            htmlNode = htmlNode[0];
            var htmlTable = '<table class="table table-bordered table-hover table-condensed table-striped">';
            htmlTable += '<thead><tr class="info text-center">';
            htmlTable += '<th>客户</th>';
            htmlTable += '<th>包号</th>';
            htmlTable += '<th>内部货号</th>';
            htmlTable += '<th>产品名称</th>';

            htmlTable += '<th>毛重</th>';
            htmlTable += '<th>净重</th>';
            htmlTable += '<th>质检净重</th>';
            htmlTable += '<th>数量/重量</th>';
            htmlTable += '<th>退货数量/重量</th>';
            htmlTable += '<th>换货数量/重量</th>';
            htmlTable += '<th>返回总重量</th>';

            htmlTable += '</tr></thead>';
            htmlTable += '<tbody><tr class="text-center">';
            htmlTable += '<td>'+data.partner+'</td>';
            htmlTable += '<td>'+data.name+'</td>';
            htmlTable += '<td>'+data.product_code+'</td>';
            htmlTable += '<td>'+data.product+'</td>';
            htmlTable += '<td>'+data.weight+'</td>';
            htmlTable += '<td>'+data.net_weight+'</td>';
            htmlTable += '<td><input  class="check-weight-data" name="check_weight" id="check_weight" data-lineid="'+data.id+'" value="'+data.check_weight+'"></td>';
            htmlTable += '<td>'+data.qty+'</td>';
            htmlTable += '<td><input  class="back-qty-data" name="back_qty" id="back_qty" data-lineid="'+data.id+'" value="'+data.back_qty+'"></td>';
            htmlTable += '<td><input  class="exchange-qty-data" name="exchange_qty" id="exchange_qty" data-lineid="'+data.id+'" value="'+data.exchange_qty+'"></td>';
            htmlTable += '<td><input  class="check-weight-data" name="back_weight" id="back_weight" data-lineid="'+data.id+'" value="'+data.back_weight+'"></td>';

            htmlTable += '</tr></tbody>';
            htmlTable += '</table>';
            htmlNode.innerHTML = htmlTable;


        }
    };
    local.HomePage = instance.Widget.extend({
        events:{
            'click #search-wait-check-order':'search_wait_check_order',
            'click #change-check-customer':"change_check_customer",
            'click #current-customer-wait-check-order':'current_customer_wait_check_order',
            'click .customer-order-wait-check':'add_customer_order_check',
            'click #current-customer-order-line':'current_customer_order_line',
            'click .current-order':"display_check_page",
            'mouseup .check-weight-data':'lock_wigth_obj',
            'blur .check-weight-data':'unlock_wigth_obj',
            'change #check-order-search':"search_check_order",
            'click #customer-quality-check-button':'package_quality_check_done'


        },

        start:function(){
            var self = this;
            var tcom_ob = $("#tcom_OB");
            if (tcom_ob[0]==undefined){
                var innerHTML = '<object id="tcom_OB" classid="clsid:987F8440-C95B-46EC-8CE5-C653E47593D5" width="0" height="0" >'
                        +'<embed id="tcom_EM" type="application/x-comm-nptcomm" width="0" height="0" pluginspage="/files/TComm.exe"></object>';
                $(innerHTML).appendTo("body");
            }

            var htmlValues={};
            tcommUtil.COMLI = 3;
            tcommUtil.init();
            console.log(qualityModel);
            qualityModel.call('get_check_customer_info',{context: new instance.web.CompoundContext()}).then(function(result){
                console.log(result);
                if (result.code =='success'){
                    htmlValues.currentCustomer = result.currentCustomer;
                    htmlValues.lastCustomerList = result.lastCustomerList;
                    htmlValues.currentOrder = result.currentOrder;
                    self.$el.append(QWeb.render("QutQualityTemplate",htmlValues));
                    var currentOrder = $(".current-order");
                    //若存在待捡订单显示输入框
                    if (currentOrder.length>0){
                        currentOrder = currentOrder[0];
                        gen_check_order_search_html();

                    }
                }
            });

        },
        package_quality_check_done:function(e){
            var check_weight = $("#check_weight");
            var line_id = '';
            if (check_weight.length>0){

                line_id = check_weight[0].dataset['lineid'];
                check_weight = check_weight.val();
                if (Reg.test(check_weight)==false){
                    alert('"质检净重"只能为数字');
                    return
                }
                if (parseInt(check_weight*100)<0){
                    alert('请输入大于0的"质检净重"数据');
                    return
                }

            }
            var back_qty = $("#back_qty");
            if (back_qty.length>0){
                back_qty = back_qty.val();
                if (Reg.test(back_qty)==false){
                    alert('退货"数量"或"重量"只能为数字');
                    return
                }
                if (parseInt(back_qty*100)<0){
                    alert('请输入大于0的退货"数量"或"重量"数据');
                    return
                }
            }
            var exchange_qty = $("#exchange_qty");
            if (exchange_qty.length>0){
                exchange_qty = exchange_qty.val();
                if (Reg.test(exchange_qty)==false){
                    alert('换货"数量"或"重量"只能为数字');
                    return
                }
                if (parseInt(exchange_qty*100)<0){
                    alert('请输入大于0的换货"数量"或"重量"数据');
                    return
                }
            }
            var back_weight = $("#back_weight");
            if (back_weight.length>0){
                back_weight = back_weight.val();
                if (Reg.test(back_weight)==false){
                    alert('换货"重量"只能为数字');
                    return
                }
                if (parseInt(back_weight*100)<0){
                    alert('请输入大于0的"重量"数据');
                    return
                }
            }
            qualityModel.call('quality_order_check_weight_done',[line_id,check_weight,back_qty,exchange_qty,back_weight],{context: new instance.web.CompoundContext()}).then(function(result){
                console.log(result);
                if (result =='failed'){
                    $("#waring-info").innerHTML ="数据写入失败";
                }else{
                    $("#waring-info").innerHTML ="数据写入成功";
                }
            });
        },
        lock_wigth_obj:function(e){
            wigthObj = e;
        },
        unlock_wigth_obj:function(e){
            wigthObj = null;
        },
        current_customer_order_line :function(e){
            $(".list-group-item").removeClass("active");
            $("#current-customer-order-line").addClass("active");
            var search = $("#check-order-search");
            clear_main_info_action();
            if (search.length>0){
                search[0].value = "";
            }
            gen_check_order_search_html();
            qualityModel.call('get_all_check_order_line',[],{context: new instance.web.CompoundContext()}).then(function(result){
                if(result.code =='success'){
                    list_quality_check_order_line(result.data);
                }else{
                    gen_waring_info(result.message);
                }
            });
        },
        search_check_order:function(e){
            $(".list-group-item").removeClass("active");
            var packageNum  = e.currentTarget.value;
            packageNum = packageNum.trim();
            if (packageNum!=""){
                clear_main_info();
                gen_waring_info("");
                qualityModel.call("get_one_check_package",[packageNum],{context:new instance.web.CompoundContext()}).then(function(result){

                    if(result.code=='success'){
                        gen_quality_check_table(result.data);
                        gen_main_info_action();
                    }else{
                        gen_waring_info(result.message);
                        clear_main_info_action();
                    }
                });
            }
        },
        display_check_page:function(e){
            gen_check_order_search_html();
            clear_main_info();
        },
        update_customer_list:function(){
            qualityModel.call('')
        },

        add_customer_order_check:function(e){

            var order_id = e.currentTarget.attributes['id'].value;
            order_id = order_id.split('-')[1];
            qualityModel.call('add_customer_order_check',[order_id],{context: new instance.web.CompoundContext()}).then(function(result){
                if(result=='success'){
                    location.reload();
                }
            });

        },
        current_customer_wait_check_order:function(e){
            $(".list-group-item").removeClass("active");
            $("#current-customer-wait-check-order").addClass("active");
            gen_top_title_info();
            clear_main_info();
            qualityModel.call('get_current_customer_all_wait_order',[],{context:new instance.web.CompoundContext()}).then(function(result){
                if (result.code=='success'){
                    display_search_wait_check_order(result.data);
                }else{
                    gen_waring_info(result.message);
                }
            });
        },
        change_check_customer:function(e){
            $(".list-group-item").removeClass("active");
            $("#change-check-customer").addClass("active");
            clear_main_info();

        },
        search_wait_check_order:function(e){
            $(".list-group-item").removeClass("active");
            $("#search-wait-check-order").addClass("active");
            clear_main_info();
            gen_top_title_info();
            qualityModel.call('get_wait_check_order',[],{context: new instance.web.CompoundContext()}).then(function(result){
                if (result.code=='success'){
                    display_search_wait_check_order(result.data);
                }
            });
        },

    });
    instance.web.client_actions.add("Out_Quality","instance.out_picking_quality.HomePage");
}