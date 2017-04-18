openerp.batar_mobile_pick_weigh = function(instance,local){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var stockWeighModel = new instance.web.Model("pick.stock.weigh");
    var wigthObj = null;
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
                alert("无效编码格式 ASCII !");
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
    gen_pick_weigh_html = function(){
        var htmlNode = $("#weigh-page-right-top");
        if (htmlNode.length>0){
            htmlNode = htmlNode[0];
            var qualityCheckHTML = '<div class="text-center">';
            qualityCheckHTML+= '<h1 class="weigh-title">入库拆包称重</h1>';
            qualityCheckHTML += '<label for="pick-package-number">请输入包号:</label>';
            qualityCheckHTML += '<input id="pick-package-number" class="package-number">';
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
    gen_pick_mobile_weigh_table = function(data_list){
        var htmlNode = $('#weigh-info');
        if (htmlNode.length>0){
            htmlNode = htmlNode[0];
            var htmlTable = '<table class="table table-bordered table-hover table-condensed table-striped">';
            htmlTable += '<thead><tr class="info text-center">';
            htmlTable += '<th>包号</th>';
            htmlTable += '<th>内部货号</th>';
            htmlTable += '<th>数量</th>';
            htmlTable += '<th>净重(g)</th>';
            htmlTable += '<th>目标库位</th>';
            htmlTable += '<th>序号</th>';
            htmlTable += '<th>拆分后盘位</th>';
            htmlTable += '<th>产品名称</th>';
            htmlTable += '</tr></thead>';

            htmlTable += '<tbody>';
            for(var i=0;i<data_list.length;i++){
                htmlTable += '<tr>';
                var data = data_list[i];
                htmlTable += '<td>'+data.package+'</td>';
                htmlTable += '<td>'+data.product_code+'</td>';

                htmlTable += '<td>'+data.qty+'</td>';
                htmlTable += '<td><input   class="receive-weight-data" name="weight" id="weight" data-lineid="'+data.id+'" value="'+data.net_weight+'"></td>';
                htmlTable += '<td>'+data.location_id+'</td>';
                htmlTable += '<td>'+data.sequence+'</td>';
                htmlTable += '<td>'+data.src_location+'</td>';
                htmlTable += '<td>'+data.product_name+'</td>';
                htmlTable += '</tr>';
            }


            htmlTable += '</tbody>';
            htmlTable += '</table>';
            htmlNode.innerHTML = htmlTable;
            pick_weigh_info_action();
        }
    };

    local.HomePage = instance.Widget.extend({
        events:{
            'click #pick-check-weigh':'pick_check_weigh',
            'change #pick-package-number':'pick_package_number',
            'click #pick-weigh-done':'pick_weigh_done',
            'mouseup .receive-weight-data':'lock_wigth_obj',
            'blur .receive-weight-data':'unlock_wigth_obj',
        },
        lock_wigth_obj:function(e){
            wigthObj = e;
        },
        unlock_wigth_obj:function(e){
            wigthObj = null;
        },
        pick_weigh_done:function(e){
            var noedeList = $(".receive-weight-data");
            var param = {};
            if(noedeList.length>0){
                for(var i=0;i<noedeList.length;i++){
                    var id = noedeList[i].dataset.lineid;
                    var value = noedeList[i].value;

                    if (Reg.test(value)==false){
                        alert("净重只能输入数字，请检查");
                        return
                    }
                    var floatValue =  parseFloat(value);
                    if (parseInt(floatValue*100)<1){
                        alert("净重必须大于0");
                        return
                    }
                    param[id] = floatValue;

                }
                stockWeighModel.call('write_weight_info',[param],{context: new instance.web.CompoundContext()}).then(function(result){
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
        pick_package_number:function(e){
            var packageNum = e.currentTarget.value;
            var infoNode = $("#waring-info");
            if (infoNode.length>0){
                infoNode = infoNode[0];
                infoNode.innerHTML = "";
            }
            if (packageNum.length>0){
                stockWeighModel.call('search_pick_package',[packageNum],{context: new instance.web.CompoundContext()}).then(function(result){
                    if (result.code=='success'){
                        var data = result.data;
                        gen_pick_mobile_weigh_table(data);
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
                            node[0].innerHTML ='<p class="text-center">该包号不存在</p>';
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
                    node[0].innerHTML ='<p class="text-center">该包号不存在</p>';
                }
            }
        },
        pick_check_weigh:function(e){
            tcommUtil.openComPort();
            var self =this;
            $(".list-group-item").removeClass("active");
            $("#pick-check-weigh").addClass("active");
            gen_pick_weigh_html();
        },
        start:function(){
            var self = this;
            var tcom_ob = $("#tcom_OB");
            if (tcom_ob[0]==undefined){
                var innerHTML = '<object id="tcom_OB" classid="clsid:987F8440-C95B-46EC-8CE5-C653E47593D5" width="0" height="0"  >'
                        +'<embed id="tcom_EM" type="application/x-comm-nptcomm" width="0" height="0" pluginspage="/files/TComm.exe"></object>';
                $(innerHTML).appendTo("body");

            }
            var htmlValues={};
            tcommUtil.COMLI = 3;
            tcommUtil.init();
            self.$el.append(QWeb.render("BatarPickStockWeighTemplate",htmlValues));
        },
    });
    instance.web.client_actions.add("pick_stock_weigh","instance.batar_mobile_pick_weigh.HomePage");
}