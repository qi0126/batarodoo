openerp.batar_stock_weigh = function(instance,local){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var stockWeighModel = new instance.web.Model("stock.weigh");
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
                console.log('获取2：' + dat);
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

                }else{
                    var kgCount = dat;
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


    var clear_right_info=function(){
         var htmlNode = $("#weigh-page-right-top");
         if (htmlNode.length>0){
                htmlNode = htmlNode[0];
                htmlNode.innerHTML = "";
         }
        var node = $("#weigh-info");
        if (node.length>0){
                node = node[0];
                node.innerHTML = "";
         }
        node = $("#weigh-info-action");
        if (node.length>0){
                node = node[0];
                node.innerHTML = "";
         }
        node = $("#waring-info");
        if (node.length>0){
                node = node[0];
                node.innerHTML = "";
         }

    };


    var update_clear_pick_in_info = function(plateNumber,clearPkg){
            var node = $(".plate-info");
            if (node.length>0){
                node = node[0];
                node.innerHTML = plateNumber;
            }
            var infoNode = $("#weigh-info");
            if (infoNode.length>0){
                infoNode = infoNode[0];
                infoNode.innerHTML = "";
            }
            var actionNode = $("#weigh-info-action");
            if (actionNode.length>0){
                actionNode = actionNode[0];
                actionNode.innerHTML = "";
            }
            if (clearPkg==true){
                var inputNode = $("#pick-in-package-number");
                if (inputNode.length>0){
                    inputNode = inputNode[0];
                    inputNode.value = "";
                }
            }
     };
    var clear_quality_line_info = function(clearPkg){
        var node = $("#weigh-info");
        if (node.length>0){
            node[0].innerHTML ="";
        }
        var node = $("#weigh-info-action");
        if (node.length>0){
            node[0].innerHTML ="";
        }
        if (clearPkg==true){
            var inputNode = $("#quality-package-number");

            if (inputNode.length>0){
                inputNode = inputNode[0];
                inputNode.value = "";
            }
        }

    };
    var gen_quality_check_line_html = function(){
        var html = '<tr class="quality-check-line">'
                +'<td><input name="qty" placeholder="检测数量"/></td>'
                +'<td><input class="receive-weight-data" name="net_weight" placeholder="检测净重"/></td>'
                +'<td><input class="receive-weight-data"  name="gross_weight" placeholder="检测毛重"/></td>'
                +'<td>'+reasonOption+'</td>'
                +'</tr>';
        return html;
    };
    var gen_quality_check_line = function(){
        var actionNode = $("#weigh-info-action");
            if (actionNode.length>0){
                actionNode = actionNode[0];
                var html = '<div >'
                    +'<table class="table table-bordered table-hover table-condensed table-striped">'
                    +'<thead><tr><td>数量</td><td>净重</td><td>毛重</td><td>结果</td></tr></thead>'
                    +'<tbody id="quality-check-table">'
                    + gen_quality_check_line_html();
                html += '</tbody>'
                    +'</table>'
                    +'<button class="btn btn-primary check-button" id="add-quality-check-line" type="button">添加质检记录</button>'
                    +'<div><button class="btn btn-success check-button" id="quality-check-ok" type="button">合格</button>'
                    +'<button class="btn btn-danger check-button" id="quality-check-not" type="button">不合格</button>'
                    +'</div>'
                    +'</div>';
                actionNode.innerHTML = html
            }
    };
    var pick_out_weigh_html=function(){
        var htmlNode = $("#weigh-page-right-top");
        if (htmlNode.length>0){
            htmlNode = htmlNode[0];
            var qualityCheckHTML = '<div class="text-center">';
            qualityCheckHTML+= '<h1 class="weigh-title">出库称重</h1>';
            qualityCheckHTML += '<label for="pick-out-package-number">请输入包号:</label>';
            qualityCheckHTML += '<input id="pick-out-package-number" class="package-number">';
            qualityCheckHTML += '</div>';
            htmlNode.innerHTML = qualityCheckHTML;
        }
    };

    var gen_pick_in_order_weigh_html=function(plateNumber){
        var htmlNode = $("#weigh-page-right-top");
        if (htmlNode.length>0){
            htmlNode = htmlNode[0];
            var pickInHTML = '<div class="text-center">';
            pickInHTML+= '<h1 class="weigh-title">入库称重分盘</h1>';
            pickInHTML += '<label for="pick-in-package-number">请输入包号:</label>';
            pickInHTML += '<input id="pick-in-package-number" class="package-number">';
            pickInHTML += '</div>';
            pickInHTML += '<div class="text-center">';
            pickInHTML += '<h4 >当前盘号:<strong class="plate-info">'+plateNumber+'</strong></h4>';
            pickInHTML += '<button class="btn btn-primary quality-check-button" id="change-plate" type="button">换盘</button>';
            pickInHTML += '<button class="btn btn-primary quality-check-button" id="split-plate-done" type="button">分盘结束</button>';
            pickInHTML += '</div>';
            htmlNode.innerHTML = pickInHTML;
        }
    };
    var gen_quality_check_weigh_html=function(plateNumber){
        var htmlNode = $("#weigh-page-right-top");
        if (htmlNode.length>0){
            htmlNode = htmlNode[0];
            var qualityCheckHTML = '<div class="text-center">';
            qualityCheckHTML+= '<h1 class="weigh-title">入库质检</h1>';
            qualityCheckHTML += '<label for="quality-package-number">请输入包号:</label>';
            qualityCheckHTML += '<input id="quality-package-number" class="package-number">';
            qualityCheckHTML += '</div>';
            htmlNode.innerHTML = qualityCheckHTML;
        }

    };
    var pick_weigh_info_action = function(){
        var htmlNode = $("#weigh-info-action");
        if (htmlNode.length>0){
            htmlNode = htmlNode[0];
            var htmlAction = '<div class="text-center">';
            htmlAction += '<button class="btn btn-primary quality-check-button" id="pick-weigh-done" type="button">确定</button>';
            htmlAction += '</div>';
            htmlNode.innerHTML = htmlAction;
        }
    };

    var gen_pick_in_order_weigh = function(data){

        var htmlNode = $('#weigh-info');
        if (htmlNode.length>0){
            htmlNode = htmlNode[0];
            var htmlTable = '<table class="table table-bordered table-hover table-condensed table-striped">';
            htmlTable += '<thead><tr class="info text-center">';
            htmlTable += '<th>包号</th>';
            htmlTable += '<th>内部货号</th>';
            htmlTable += '<th>数量</th>';
            htmlTable += '<th>毛重(g)</th>';
            htmlTable += '<th>净重(g)</th>';
            htmlTable += '<th>实际数量</th>';
            htmlTable += '<th>实际毛重(g)</th>';
            htmlTable += '<th>实际净重(g)</th>';
            htmlTable += '<th>产品名称</th>';
            htmlTable += '</tr></thead>';

            htmlTable += '<tbody><tr>';

            htmlTable += '<td>'+data.package_num+'</td>';
            htmlTable += '<td>'+data.default_code+'</td>';
            htmlTable += '<td>'+data.product_qty+'</td>';
            htmlTable += '<td>'+data.gross_weight+'</td>';
            htmlTable += '<td>'+data.net_weight+'</td>';
            htmlTable += '<td><input   name="product_qty" id="product_qty"  data-lineid="'+data.id+'" value="'+data.actual_product_qty+'"></td>';
            htmlTable += '<td><input   class="receive-weight-data" name="weight" id="actual_gross_weight" data-lineid="'+data.id+'" value="'+data.actual_gross_weight+'"></td>';
            htmlTable += '<td><input  class="receive-weight-data" name="net_weight" id="actual_net_weight" data-lineid="'+data.id+'" value="'+data.actual_net_weight+'"></td>';

            htmlTable += '<td>'+data.product_name+'</td>';
            htmlTable += '</tr></tbody>';
            htmlTable += '</table>';
            htmlTable += '<div class="text-center"><button class="btn btn-primary " id="pick_in_order_weigh_done" type="button">确认</button></div>';
            htmlNode.innerHTML = htmlTable;
        }
    };
    var  gen_pick_check_weigh_table = function(data){
        var htmlNode = $('#weigh-info');
        if (htmlNode.length>0){
            htmlNode = htmlNode[0];
            var htmlTable = '<table class="table table-bordered table-hover table-condensed table-striped">';
            htmlTable += '<thead><tr class="info text-center">';
            htmlTable += '<th>客户</th>';
            htmlTable += '<th>包号</th>';
            htmlTable += '<th>内部货号</th>';
            htmlTable += '<th>数量</th>';
            htmlTable += '<th>毛重(g)</th>';
            htmlTable += '<th>净重(g)</th>';

            htmlTable += '<th>产品名称</th>';
            htmlTable += '</tr></thead>';

            htmlTable += '<tbody><tr>';
            htmlTable += '<td>'+data.partner_name+'</td>';
            htmlTable += '<td>'+data.name+'</td>';
            htmlTable += '<td>'+data.product_code+'</td>';
            htmlTable += '<td>'+data.qty+'</td>';
            htmlTable += '<td><input  class="receive-weight-data" name="weight" id="weight" data-lineid="'+data.id+'" value="'+data.weight+'"></td>';
            htmlTable += '<td><input  class="receive-weight-data" name="net_weight" id="net_weight" data-lineid="'+data.id+'" value="'+data.weight+'"></td>';

            htmlTable += '<td>'+data.product_name+'</td>';
            htmlTable += '</tr></tbody>';
            htmlTable += '</table>';
            htmlNode.innerHTML = htmlTable;
            pick_weigh_info_action();
        }
    };

    var gen_quality_check_weigh_table = function(data){
        var htmlNode = $('#weigh-info');
        if (htmlNode.length>0){
            htmlNode = htmlNode[0];
            var htmlTable = '<table class="table table-bordered table-hover table-condensed table-striped">';
            htmlTable += '<thead><tr class="info text-center">';
            htmlTable += '<th>包号</th>';
            htmlTable += '<th>接收数量</th>';
            htmlTable += '<th>接收净重(g)</th>';
            htmlTable += '<th>接收毛重(g)</th>';

            htmlTable += '<th>内部货号</th>';
            htmlTable += '<th>产品名称</th>';


            htmlTable += '<th>状态</th>';

            htmlTable += '</tr></thead>';
            htmlTable += '<tbody><tr>';
            htmlTable += '<td>'+data.package_num+'</td>';
            htmlTable += '<td>'+data.product_qty+'</td>';
            htmlTable += '<td>'+data.net_weight+'</td>';
            htmlTable += '<td>'+data.gross_weight+'</td>';
            htmlTable += '<td>'+data.default_code+'</td>';
            htmlTable += '<td>'+data.product_name+'</td>';


            htmlTable += '<td>'+data.state+'</td>';
            htmlTable += '</tr></tbody>';
            htmlTable += '</table>';
            htmlNode.innerHTML = htmlTable;


        }
    };
    local.HomePage = instance.Widget.extend({
        events:{
            'click #quality-check':'quality_check',
            'change #quality-package-number':"change_quality_package_number",
            'click #change-plate':'change_plate',
            'click #split-plate-done':'split_plate_done',
            'mouseup .receive-weight-data':'lock_wigth_obj',
            'blur .receive-weight-data':'unlock_wigth_obj',
            'click #pick-out-order-weigh':'pick_out_order_weigh',
            'change #pick-out-package-number':'change_pick_out_package_number',
            'click #pick-weigh-done':'pick_weigh_done',
            'click #mobile-pick-in-order-weigh':'pick_in_order_line_weigh',
            'change #pick-in-package-number':'change_pick_in_package_number',
            'click #pick_in_order_weigh_done':'pick_in_order_weigh_done',
            'click #add-quality-check-line':'add_quality_check_line',
            'click #quality-check-ok':'quality_check_ok',
            'click #quality-check-not':'quality_check_not',




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
            self.$el.append(QWeb.render("BatarStockWeighTemplate",htmlValues));
        },
        quality_check_ok:function(e){

            var self = this;
            var trNodes = $('.quality-check-line');
            var check_data_list = [];
            var len = trNodes.length;
            for(var i=0;i<len;i++){
                var tr = trNodes[i];
                var tds = tr.children;

                var qty = tds[0].children[0].value || 0;
                var net_weight = tds[1].children[0].value || 0;
                var gross_weight = tds[2].children[0].value || 0;
                var reason = tds[3].children[0].value || 0;
                var floatQty=  parseFloat(qty);
//                console.log("======================");
//                console.log(qty);
//                console.log(Reg.test(qty));
                if (Reg.test(qty)==false){
                    alert('"数量"或"重量"只能为数字');
                    return
                }
                if (parseInt(floatQty*100)<1){
                    alert('请输入大于0的"数量"或"重量"数据');
                    return
                }
                var floatNetWeight=  parseFloat(net_weight);
                if (Reg.test(net_weight)==false){
                    alert('"净重"只能输入数字，请检查');
                    return
                }
                if (parseInt(floatNetWeight*100)<1){
                    alert('请输入大于0的"净重"数据');
                    return
                }
//                var floatGrossWeight=  parseFloat(gross_weight);
//               if (Reg.test(gross_weight)==false){
//                    alert('"毛重"只能输入数字，请检查');
//                    return
//                }
//                if (parseInt(floatGrossWeight*100)<1){
//                    alert('请输入大于0的"毛重"数据');
//                    return
//                }

                check_data_list.push({
                    qty:qty,
                    net_weight:net_weight,
                    gross_weight:gross_weight,
                    reason:reason,
                })

            }
            var packageNum = "";
            var pakgNum = $("#quality-package-number");
            if (pakgNum.length>0){
                packageNum = pakgNum[0].value;
            }
            stockWeighModel.call('quality_check_ok',[packageNum,check_data_list],{context: new instance.web.CompoundContext()}).then(function(result){
                if (result == 'success'){
                    clear_quality_line_info(true);
                }else{
                    var node = $("#waring-info");
                    if (node.length>0){
                        node = node[0];
                        node.innerHTML ='<p>写入失败，请联系管理员</p>';
                    }
                }
            });

        },
        quality_check_not:function(e){
            var self = this;
            var trNodes = $('.quality-check-line');
            var check_data_list = [];
            var len = trNodes.length;
            for(var i=0;i<len;i++){
                var tr = trNodes[i];
                var tds = tr.children;
                var qty = tds[0].children[0].value || 0;
                var net_weight = tds[1].children[0].value || 0;
                var gross_weight = tds[2].children[0].value || 0;
                var reason = tds[3].children[0].value || 0;
                var floatQty=  parseFloat(qty);
                if (Reg.test(qty)==false){
                    alert('"数量"或"重量"只能为数字');
                    return
                }
                if (parseInt(floatQty*100)<1){
                    alert('请输入大于0的"数量"或"重量"数据');
                    return
                }
                var floatNetWeight=  parseFloat(net_weight);
                if (Reg.test(net_weight)==false){
                    alert('"净重"只能输入数字，请检查');
                    return
                }
                if (parseInt(floatNetWeight*100)<1){
                    alert('请输入大于0的"净重"数据');
                    return
                }
                var floatGrossWeight=  parseFloat(gross_weight);
               if (Reg.test(gross_weight)==false){
                    alert('"毛重"只能输入数字，请检查');
                    return
                }
                if (parseInt(floatGrossWeight*100)<1){
                    alert('请输入大于0的"毛重"数据');
                    return
                }
                check_data_list.push({
                    qty:qty,
                    net_weight:net_weight,
                    gross_weight:gross_weight,
                    reason:reason,
                })

            }
            var packageNum = "";
            var pakgNum = $("#quality-package-number");
            if (pakgNum.length>0){
                packageNum = pakgNum[0].value;
            }
            stockWeighModel.call('quality_check_not',[packageNum,check_data_list],{context: new instance.web.CompoundContext()}).then(function(result){
                if (result == 'success'){
                    clear_quality_line_info(true);
                }else{
                    var node = $("#waring-info");
                    if (node.length>0){
                        node = node[0];
                        node.innerHTML ='<p>写入失败，请联系管理员</p>';
                    }
                }
            });
        },

        add_quality_check_line:function(e){
            var self = this;
            var recordNode = $("#quality-check-table");

            if(recordNode.length>0){

                recordNode.append(gen_quality_check_line_html());

            }

        },
        pick_in_order_weigh_done:function(e){
            console.log(e);
            var self = this;
            var productQty = 0;
            var netWeight = 0;
            var grossWeight = 0;
            var lineId = null;
            var node = $(".plate-info");
            var plateNumber = "";
            if (node.length>0){
                node = node[0];
                plateNumber = node.innerText;
            }
            if (plateNumber==""){
                alert("请点击换盘按钮获得盘号");
                return
            }
            var productQtyNode = $("#product_qty");
            if (productQtyNode){
                    productQtyNode = productQtyNode[0];
                    productQty = productQtyNode.value;
                    lineId = productQtyNode.dataset.lineid;
            }
            var netWeightNode= $("#actual_net_weight");
            if (netWeightNode ){
                    netWeightNode = netWeightNode[0];
                    netWeight = netWeightNode.value;
            }
            var grossWeightNode = $("#actual_gross_weight");
            if (grossWeightNode){
                    grossWeightNode = grossWeightNode[0];
                    grossWeight = grossWeightNode.value;
            }
            var floatQty=  parseFloat(productQty);
                if (Reg.test(productQty)==false){
                    alert('"数量"或"重量"只能为数字');
                    return
                }
                if (parseInt(floatQty*100)<1){
                    alert('请输入大于0的"数量"或"重量"数据');
                    return
                }
                var floatNetWeight=  parseFloat(netWeight);
                if (Reg.test(netWeight)==false){
                    alert('"净重"只能输入数字，请检查');
                    return
                }
                if (parseInt(floatNetWeight*100)<1){
                    alert('请输入大于0的"净重"数据');
                    return
                }
                var floatGrossWeight=  parseFloat(grossWeight);
               if (Reg.test(grossWeight)==false){
                    alert('"毛重"只能输入数字，请检查');
                    return
                }
                if (parseInt(floatGrossWeight*100)<1){
                    alert('请输入大于0的"毛重"数据');
                    return
                }
            stockWeighModel.call('pick_in_order_weigh_done',[lineId,netWeight,grossWeight,productQty],{context: new instance.web.CompoundContext()}).then(function(result){
                    if (result == 'success'){
                        var node = $("#waring-info");
                        if (node.length>0){
                            node = node[0];
                            node.innerHTML ='<p>写入成功</p>';
                        }
                    }else{
                        var node = $("#waring-info");
                        if (node.length>0){
                            node = node[0];
                            node.innerHTML ='<p>写入失败，请联系管理员</p>';
                        }
                    }
                });

        },
        change_pick_in_package_number:function(e){
            var packageNum = e.currentTarget.value;
            var node = $("#waring-info");
            if (node.length>0){
                node = node[0];
                node.innerHTML ='';
            }
            if (packageNum.length>0){
                stockWeighModel.call('search_pick_in_order_package',[packageNum],{context: new instance.web.CompoundContext()}).then(function(result){
                    console.log(result);
                    if (result.code=='success'){
                        gen_pick_in_order_weigh(result.data);
                        node = $("#waring-info");
                        if (node.length>0){
                            node[0].innerHTML =' ';
                        }

                    }else{
                        var node = $("#weigh-info");
                        if (node.length>0){
                            node[0].innerHTML ='';
                        }
                        node = $("#weigh-info-action");
                        if (node.length>0){
                            node[0].innerHTML ="";
                        }
                        node = $("#waring-info");
                        if (node.length>0){
                            node[0].innerHTML ='<p class="text-center">该包号不存在或者该包不为"等待分盘"状态</p>';
                        }
                    }
                });
            }else{
                var node = $("#weigh-info");
                if (node.length>0){
                    node[0].innerHTML ="";
                }
                node = $("#weigh-info-action");
                if (node.length>0){
                    node[0].innerHTML ="";
                }
                node = $("#waring-info");
                if (node.length>0){
                   node[0].innerHTML ='<p class="text-center">该包号不存在或者该包不为"等待分盘"状态</p>';
                }
            }

        },
        pick_in_order_line_weigh:function(e){
            tcommUtil.openComPort();
            clear_right_info();
            $(".list-group-item").removeClass("active");
            $("#mobile-pick-in-order-weigh").addClass("active");
            stockWeighModel.call('get_plate',[],{context: new instance.web.CompoundContext()}).then(function(plateNumber){
                gen_pick_in_order_weigh_html(plateNumber);
            });

        },
        lock_wigth_obj:function(e){
            wigthObj = e;
        },
        unlock_wigth_obj:function(e){
            wigthObj = null;
        },

        pick_weigh_done:function(e){
            var netWeight = 0;
            var grossWeight = 0;
            var lineId = null;
            var netWeightNode= $("#net_weight");
            if (netWeightNode.length>0){
                    netWeightNode = netWeightNode[0];
                    netWeight = netWeightNode.value;
            }
            var grossWeightNode = $("#weight");
            if (grossWeightNode.length>0){
                    grossWeightNode = grossWeightNode[0];
                    grossWeight = grossWeightNode.value;
                    lineId = grossWeightNode.dataset.lineid;
            }
            if (lineId!=null || lineId!=undefined){
                stockWeighModel.call('pick_weigh_done',[lineId,netWeight,grossWeight],{context: new instance.web.CompoundContext()}).then(function(result){
                    if (result == 'success'){
                        var node = $("#waring-info");
                        if (node.length>0){
                            node = node[0];
                            node.innerHTML ='<p>写入成功</p>';
                        }
                    }else{
                        var node = $("#waring-info");
                        if (node.length>0){
                            node = node[0];
                            node.innerHTML ='<p>写入失败，请联系管理员</p>';
                        }
                    }
                });
            }

        },
        change_pick_out_package_number:function(e){
            var packageNum = e.currentTarget.value;
            if (packageNum.length>0){
                stockWeighModel.call('search_pick_out_package',[packageNum],{context: new instance.web.CompoundContext()}).then(function(result){
                    if (result.code=='success'){
                        gen_pick_check_weigh_table(result.data);
                        node = $("#waring-info");
                        if (node.length>0){
                            node[0].innerHTML =' ';
                        }

                    }else{
                        var node = $("#weigh-info");
                        if (node.length>0){
                            node[0].innerHTML ='';
                        }
                        node = $("#weigh-info-action");
                        if (node.length>0){
                            node[0].innerHTML ="";
                        }
                        node = $("#waring-info");
                        if (node.length>0){
                            node[0].innerHTML ='<p class="text-center">该包号不存在或者该包不为等待质检状态</p>';
                        }
                    }
                });
            }else{
                var node = $("#weigh-info");
                if (node.length>0){
                    node[0].innerHTML ="";
                }
                node = $("#weigh-info-action");
                if (node.length>0){
                    node[0].innerHTML ="";
                }
                node = $("#waring-info");
                if (node.length>0){
                   node[0].innerHTML ='<p class="text-center">该包号不存在或者该包不为等待质检状态</p>';
                }
            }

        },
        pick_out_order_weigh:function(e){
            var self =this;
            tcommUtil.openComPort();
            clear_right_info();
            $(".list-group-item").removeClass("active");
            $("#pick-out-order-weigh").addClass("active");
            pick_out_weigh_html();

        },




        change_plate:function(e){
            stockWeighModel.call('change_plate',[],{context: new instance.web.CompoundContext()}).then(function(result){
                update_clear_pick_in_info(result,true);
            });
        },
        split_plate_done:function(e){
            stockWeighModel.call('split_plate_done',[],{context: new instance.web.CompoundContext()}).then(function(result){
                update_clear_pick_in_info("",true);
            });
        },
        change_quality_package_number:function(e){
            var packageNum = e.currentTarget.value;

            var node = $("#waring-info");
            if (node.length>0){
                node[0].innerHTML ="";
            }
            if (packageNum.length>0){
                stockWeighModel.call('search_quality_package',[packageNum],{context: new instance.web.CompoundContext()}).then(function(result){
                    if (result.code=='success'){
                        var data = result.data[0];
                        gen_quality_check_weigh_table(data);
                        //添加质检记录
                        gen_quality_check_line();

                    }else{
                        clear_quality_line_info();
                        node = $("#waring-info");
                        if (node.length>0){
                           node[0].innerHTML ='<p class="text-center">该包号不存在或者该包不为等待质检状态</p>';
                        }
                    }
                });
            }else{
                 clear_quality_line_info();

            }


        },
        quality_check:function(e){
            var self =this;
            tcommUtil.openComPort();

            clear_right_info();
            //获得质检原因
            stockWeighModel.call('get_quality_reason',[],{context: new instance.web.CompoundContext()}).then(function(result){
                if (result.code = 'success'){
                    var data = result.data;
                    reasonOption = "<select name='reason' id='reason'><option value = 0>合格</option>";
                    for(var i=0;i<data.length;i++){
                         reasonOption += "<option value ="+data[i].id+">"+data[i].name+"</option>";
                    }
                     reasonOption += "</select>";
                }

                $(".list-group-item").removeClass("active");
                $("#quality-check").addClass("active");
                gen_quality_check_weigh_html();
            });

        },

    });
    instance.web.client_actions.add("stock_weigh","instance.batar_stock_weigh.HomePage");
}