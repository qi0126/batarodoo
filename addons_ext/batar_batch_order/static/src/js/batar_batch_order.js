openerp.batar_batch_order = function(instance,local){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var batchModel = new instance.web.Model('batar.batch.sale.order');
    var page_limit =10;
    var select1_num = 0;
    var needSort = null;
    //公有变量，改变款式的一个变字
    var order_add_istf =0;
    var order_add_id='';
    var input_pro_name="";
    //公有变量，“下单确认”款式数量
    var add_order_num = 0;
    var update_current_customer = function(self,customer_info){
        var currentCustomerNode = self.$el.find(".current-customer")[0];

      var html ="";
        html += '<button class="currentCustomer" id="'+customer_info.id+'">';
        html += '名称:'+customer_info.name+'<br/>';
        html += '编号:'+customer_info.code+'<br/>';
        html += '电话:'+customer_info.phone+'<br/>';
        html +='</button>';
        currentCustomerNode.innerHTML = html;
    };

    var update_customer_info_search =function(self,default_value){
        if (default_value==undefined){
            default_value = "";
        }

        var searchNode = self.$el.find('#batch_order-right-top')[0];
        var html = '<br/><div class="text-center right-input-name" >输入客户名称：<input type="text" class="search-query"  id="batch-order-customer-search" value="'+default_value+'" placeholder="客户名称/编码/电话"/></div>';
        searchNode.innerHTML = html;

    };

    //用户分页
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
            pageHtml +='<button  class="btn-sm'+pageClass+' page page-'+page_list[j]+' selectpage">'+page_list[j]+'</button>';
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
        var customer_list = customer_info_dict.customer_info;
        var customer_list_len = customer_list.length;
        var pageRightInfoNode = self.$el.find('#main-info-body')[0];

        var customerTableInfoHtml = '<table class="table table-bordered table-hover table-condensed text-center table-striped table-bordered">'
            +'<thead>'
            +'    <tr>'
            +'       <th>客户名称</th>'
            +'        <th>客户编号</th>'
            +'       <th>客户电话</th>'
            +'        </tr>'
            +'</thead>'

            +'<tbody class="table-body">';
        for(var i=0;i<customer_list_len;i++){
            customerTableInfoHtml += '<tr class="customer-table " id="customer-'+customer_list[i].id+'">'
                + '<td><span style="cursor: pointer;">'+customer_list[i].name+'</span></td>'
                + '<td><span style="cursor: pointer;">'+customer_list[i].customer_code+'</span></td>'
                + '<td><span style="cursor: pointer;">'+customer_list[i].phone+'</span></td>'
                + '</tr>';
        }
        customerTableInfoHtml += '</tbody></table>';
        customerTableInfoHtml += gen_customer_info_page(customer_info_dict.page_list,customer_info_dict.current_page,customer_info_dict.page_last);
        pageRightInfoNode.innerHTML =  customerTableInfoHtml;
    };

    //页面加载“添加套路定制下单”js
    var model_load=function(){
		//左方"已下订单" 菜单添加
		leftmenu_prolist_html();
		//右边"添加款式“内容添加
		add_model_html();

		$("#left-menu").hide();
		$("#add-model").show();
		$("#edit-model").hide();
    }


    //左边菜单订单产品HTML
    var leftmenu_prolist_html=function(){
    	batchModel.call('get_order_product_template_list',[],{context: new instance.web.CompoundContext()}).then(function(result){
    		//结果处理判断
//    	    console.log(result);
    	    if(result.code=="success"){
	        	var leftmenu_prolist_htmlcode ='';
	        	//console.log(result.data.length);
	        	for(var i = 0 ; i<result.data.length;i++){
		        	leftmenu_prolist_htmlcode 	+='<button id="edit-model-'+result.data[i].id+'" class="edit-model-btn">'+result.data[i].name+'</button>'
	        	}
	        	$("#already-model").html(leftmenu_prolist_htmlcode);
    	    }else{
    	    	$("#already-model").html("");
    	    }
    	});

    }
    //添加款式HTML
    var add_model_html=function(){
    	var add_model_htmlcode="";
    	add_model_htmlcode 	+='<button type="button" class="btn btn-warning btn-lg btn-block">定式下单</button>'
											+'          <div class="row" style="display:none;">'
											+'           <div class="col-sm-3">'
											+'             商品大类'
											+'              <select id="select_multi_bigclass" class="select_gallery_multiple1" style="width:100%">'
											+'                <option value="手镯">手镯</option>'
											+'                <option value="机织链">机织链</option>'
											+'              <option value="坠">坠</option>'
											+'              </select>'
											+'           </div>'
											+'            <div class="col-sm-3">'
											+'           商品中类'
											+'            <select id="select_multi_middleclass" class="select_gallery_multiple1" style="width:100%">'
											+'               <option value="手镯">密口手镯</option>'
											+'                <option value="机织链">牛鼻手镯</option>'
											+'              </select>'
											+'           </div>'
											+'           <div class="col-sm-4">'
											+'            商品小类'
											+'             <select id="select_multi_smallclass" class="select_gallery_multiple1" style="width:100%">'
											+'              <option value="手镯">卜面实心密口手镯</option>'
											+'              <option value="机织链">实心密口对对镯</option>'
											+'             </select>'
											+'            </div>'
											+'    	</div>'
											+'     <hr/>'
											+'   	<div id="model-list">'
											+'       <table style="width: 100%" cellspacing="0" cellpadding="0">'
											+'					<tr>'
											+' 						<td align="center" style="text-align:right;">款式名称：</td>'
											+' 						<td>'
											+'								  <input class="input800" id="product_name"  list="productname" ></input> <button id="product_name_commit" class="btn btn-primary btnclass" style="margin-left:74px; width:194px;font-size:0.85vw">款式确认</button>'
											+'							</td>'
											+' 					</tr>'
											+'								<tr id="warry_list" style="color:red; display:none;"><td></td><td>产品查询无记录，请重新输入！</td></tr>'
											+' 					<tr>'
											+' 						<td valign="middle" style="text-align:right;">规     格：</td>'
											+' 						<td id="stand-size-html">'
											+'  						</td>'
											+'  					</tr>'
											+'			  </table>'
											+'   	</div>'
											+'          <hr/>'
											+'  	<div>'
											+'         <div id="continue_order_div" align="right" style="padding:10px;display:none;">'
											+'         	<button type="button" class="btn btn-default btnclass" onclick="location.reload(true)">取消</button>'
											+'             <button type="button" id="continue_order_btn" class="btn btn-primary btnclass">规格确认</button>'
											+'         </div>'
											+'   	</div>'
											+'  <div id="add_model_list" style="display:none;">'
													+'   <hr/>'
								        	 		+'		<button type="button" class="btn btn-primary btn-lg btn-block">产品款式列表</button>'
													+'     <div align="right" style="padding:10px;">'
													+'     	<div id="add-orderid-div" style="display:none;"></div>'
													+'         <button type="button" id="batch-del-btn" class="btn btn-warning btnclass">批量删除</button>'
													+'        <button type="button" class="btn btn-default btnclass" style="display:none;">取 消</button>'
													+'     	<button type="button" class="btn btn-primary btnclass" id="order-submit-btn">提 交</button>'
													+'     </div>'
													+' 	<table id="model_list_table_id" class="model_list_table table-striped table-bordered" cellspacing="0" cellpadding="0">'
													+'       <thead id="added-model-list-thead">'
													+'       </thead>'
													+'      <tbody id="added-model-list-html">'
													+'      </tbody>'
													+'     </table>'
													+'		<hr/>'
											+'  </div>';
    	$("#add-model").html(add_model_htmlcode);
    	$(".select_gallery_multiple1").select2();
    	$(".select_gallery_multiple3").select2();
		    datalist_html();
    	//款式名称读取接口
    	batchModel.call('get_product_template_list',["",0,10000],{context: new instance.web.CompoundContext()}).then(function(result){
    		var product_name_list ='';
    		//款式编码输入框提示
    		var datalist_proid_code ='';
    		//款式名称输入框提示
    		var datalist_proname_code ='';
    	    for(var i=0;i<result.data.length;i++){
    	    	product_name_list +='<option  value="'+result.data[i].id+'"></option>';
    	    	datalist_proid_code +='<option value="'+result.data[i].id+'"/>';
    	    	datalist_proname_code +='<option value="'+result.data[i].name+'"/>';
    	    }
    	    $("#product_name").html(product_name_list);
    	    $("#productid").html(datalist_proid_code);
    	    $("#productname").html(datalist_proname_code);
    	});
      }

    //编辑款式
    var edit_model_html=function(){
    	var edit_mode_htmlcode="";
    	edit_mode_htmlcode	+='<button type="button" class="btn btn-primary btn-lg btn-block">已下订单款式列表</button>'
											+'     <div class="row" style="display:none;">'
											+'     <div class="col-sm-3">'
											+'       商品大类'
											+'       <select id="select_multi_bigclass" class="select_gallery_multiple2" style="width:100%">'
											+'         <option value="手镯">手镯</option>'
											+'         <option value="机织链">机织链</option>'
											+'          <option value="坠">坠</option>'
											+'       </select>'
											+'     </div>'
											+'    <div class="col-sm-3">'
											+'       商品中类'
											+'       <select id="select_multi_middleclass" class="select_gallery_multiple2" style="width:100%">'
											+'         <option value="手镯">密口手镯</option>'
											+'         <option value="机织链">牛鼻手镯</option>'
											+'       </select>'
											+'     </div>'
											+'     <div class="col-sm-4">'
											+'       商品小类'
											+'      <select id="select_multi_smallclass" class="select_gallery_multiple2" style="width:100%">'
											+'          <option value="手镯">卜面实心密口手镯</option>'
											+'        		<option value="机织链">实心密口对对镯</option>'
											+'       </select>'
											+'     </div>'
											+'    <div style="padding:10px;">'
											+'       <select id="select_super_class" class="select_gallery_multiple2" multiple="multiple" style="width:100%">'
											+'         <option value="亮菠萝花">亮菠萝花</option>'
											+'          <option value="网纹">网纹</option>'
											+'         <option value="网纹间满天星">网纹间满天星</option>'
											+'         <option value="斜纹间满天星">斜纹间满天星</option>'
											+'         <option value="大刀网纹间满天星">大刀网纹间满天星</option>'
											+'        <option value="大刀斜纹满天星">大刀斜纹满天星</option>'
											+'         <option value="大刀流星雨">大刀流星雨</option>'
											+'         <option value="网纹套满天星">网纹套满天星</option>'
											+'         <option value="大刀网纹套满天星">大刀网纹套满天星</option>'
											+'      </select>'
											+'     </div>'
											+'    </div>'
											+'   <hr/>'
											+'  <div id="model_list">'
											+'    <table class="model_list_table table-striped table-bordered" cellspacing="0" cellpadding="0">'
											+'       <thead>'
											+'         <tr>'
											+'           <th style="display:none;">全选</th>'
											+'           <th style="display:none;">商品编码</th>'
											+'            <th>产品名称</th>'
											+'           <th>材 质</th>'
											+'          <th>标准克重</th>'
											+'          <th>工 费(元/克)</th>'
											+'          <th>数 量(件)</th>'
											+'           <th style="display:none;">删 除</th>'
											+'        </tr>'
											+'       </thead>'
											+'      <tbody id="added_order_list_tab">'
											+'      </tbody>'
											+'     </table>'
											+'   </div>'
											+'     <hr/>'
											+'	<div>'
											+'     <div align="right" style="padding:10px;">'
											+'         <button type="button" class="btn btn-warning btnclass" style="display:none;">批量删除</button>'
											+'        <button type="button" class="btn btn-default btnclass" style="display:none;">取 消</button>'
											+'     	 <button type="button" class="btn btn-primary btnclass" id="addedorder-submit-btn">保 存</button>'
											+'     </div>'
											+'	</div>';
						$("#edit-model").html(edit_mode_htmlcode);
						$(".select_gallery_multiple2").select2();
						datalist_html();
    };

    //页面下拉datalist
    var datalist_html=function(){
    	var datalist_htmlcode="";
    	datalist_htmlcode	+='		<!--款式名称-->'
											+'		<datalist id="productname">'
											+'		</datalist>';
    	$("#datalist-div").html(datalist_htmlcode);
    };

    //款式名单输入框输入框绘制
    var proname_submit_html=function(){
    	//获取款式名称ID
    	var proid_name = document.getElementById("product_name").value;
    	var proid_num = 0;
    	batchModel.call('get_product_template_list',[proid_name,0,10000],{context: new instance.web.CompoundContext()}).then(function(result){
    		if(result.code == "success" && result.data.length == 1){
          proid_num=result.data[0].id;
          $("#add-orderid-div").html(proid_num);
    			$("#continue_order_div").show();
    			$("#warry_list").hide();
    			$("#stand-size-html").show();
    			$("#continue_order_div").show();
	        	batchModel.call('get_product_template_attributes',[proid_num],{context: new instance.web.CompoundContext()}).then(function(result){
	        		//console.log(result);
	        		var result_code=result;
	        		var stand_code='';
	        		select1_num++;
	        		for(var i=0;i<result_code.data.length;i++){
		        			stand_code	+='  				        <div class="example">'
		        								+'							   <div id="proid_number" style="display:none;">'+proid_num+'</div>'
												+'  				           <div style="float:left;width:100px;text-align:right;"> '+result_code.data[i].name+'：</div>'
												+'                      		<select id="select_multi_id_'+result.data[i].id+'" class="select_gallery_multiple0'+select1_num+'  select-attribute" multiple="multiple" style="width:66%;height:50px;">';
		        			for(var j=0;j<result_code.data[i].data.length;j++){
		        				stand_code	+='                        			<option value="'+result_code.data[i].data[j].id+'">'+result_code.data[i].data[j].name+'</option>';
	        				}
		        			stand_code	+='                    			</select>'
												+'						     </div>';
		        			var multiple_num =".select_gallery_multiple"+i;
	        		}
	        		$("#stand-size-html").html(stand_code);
	        		var multiple_num =".select_gallery_multiple0"+select1_num;
	        		$(multiple_num).select2();
	        	});
    		}else{
    			console.log("产品查询无记录，请重新输入！");
    			$("#stand-size-html").hide();
    			$("#continue_order_div").hide();
    			$("#add_model_list").hide();
    			$("#warry_list").show();
    		}
    	});
    }


    local.HomePage = instance.Widget.extend({
        events:{
	        'click #change-customer-btn':"change_customer",
	        'change #batch-order-customer-search':'search_customer',
	        'click .customer-table':"add_current_customer_form_table",
	        'click #add-model-btn':'add_model_btn_function',
	        'click .edit-model-btn':'edit_model_table',
	        'keydown #product_name':'change_product_content',
	        'keyup #product_name':'change_product_keypress_content',
	        'click #continue_order_btn':'continue_order_function',
	        'change #allcheck-btn':'allcheck_function',
	        'click #order-submit-btn':'order_submit_function',
	        'keypress #order-submit-btn':'order_submit_keyup',
	        'click #product_name_commit':'product_name_commit_function',
	         'click .added-order-del-btn':'added_order_del_function',
	         'click #batch-del-btn':'batch_del_btn_function',
	         'click .ordernum-jian':'ordernum_jian_function',
	         'click .ordernum-add':'ordernum_add_function',
	         'click #addedorder-submit-btn':'addorder_submit_function',
	          'change .ordernum_onchange':'ordernum_onchange_function',
	          'click .selectpage':'get_customer_page_function',
        },

        start:function(){
            var self = this;
            var htmlValues={};
            batchModel.call('get_current_user_info',[0,page_limit],{context: new instance.web.CompoundContext()}).then(function(current_user_info){
                self.display_current_user_info(self,current_user_info);
            });
        },

        //分页点击用户切换
        get_customer_page_function:function(e){
        	//console.log(e.target.innerText);

            var self = this;
            // var key = e.currentTarget.value;
            var key = $("#batch-order-customer-search").val();
            //page_num页码 page_limit每页多少条记录
        	  var page_num =parseInt(e.target.innerText)-1;
            batchModel.call('get_customter_list',[page_num,page_limit,key],{context: new instance.web.CompoundContext()}).then(function(customer_info_dict){               update_customer_info_search(self,key);
                update_customer_info_table(self,customer_info_dict);
            });
        },

        //左边菜单“+添加款式”按钮事件
        add_model_btn_function:function(e){
        	var self= this;
 			//"定制下单页"继续下单
 			model_load();
        },

        //“已下单产品列表页”
        edit_model_table:function(e){
        	 var self= this;
        	var added_proid_num =(e.currentTarget.id).split("-")[2];
        	edit_model_html();
        	batchModel.call('get_order_product_product_list',[added_proid_num],{context: new instance.web.CompoundContext()}).then(function(result){
        		//结果处理判断
        	    if(result.code =="success"){
        	    	var  added_order_list_html ='';
        	    	for(var i=0;i<result.data.length;i++){
        	    		added_order_list_html	+='        <tr>'
															+'          <td style="display:none;"><input name="order_checkbox" type="checkbox"/></td>'
															+'          <td id="added-proid-sum-'+result.data[i].id+'" style="display:none;">'+result.data[i].id+'</td>'
															+'          <td>'+result.data[i].name+'</td>'
															+'          <td>'+result.data[i].product_material+'</td>'
															+'          <td>'+result.data[i].standard_weight+'</td>'
															+'          <td>'+result.data[i].real_time_price_unit+'</td>'
															+'           <td><button id="order-jian-'+result.data[i].id+'" class="btn btn-warning btn-sm ordernum-jian btn-temp">-</button><input type="text"  id="ordernum_'+result.data[i].id+'" class="input70" value="'+result.data[i].order_qty+'"></input><button  id="order-add-'+result.data[i].id+'" class="btn btn-primary btn-sm ordernum-add btn-temp">+</button></td>'
															+'           <td style="display:none;"><button type="button" class="btn btn-danger btn-sm">X</button></td>'
															+'        </tr>';
        	    	}
        	    	$("#added_order_list_tab").html(added_order_list_html);
        	    }
        	});

        	$("#left-menu").hide();
        	$("#add-model").hide();
        	$("#edit-model").show();
        },

        //款式名称input事件
        change_product_content:function(e){
        	//输入框按回车键后js
            if(e.keyCode==13){
            	//款式名单输入框输入框绘制
            	proname_submit_html();
            }
        },

       //款式名称字符改变keyon事件
       change_product_keypress_content:function(e){
         var input_proname_value =e.currentTarget.value;
         if(input_proname_value==" "){
           input_proname_value ="";
         }
         batchModel.call('get_product_template_list',[input_proname_value,0,10000],{context: new instance.web.CompoundContext()}).then(function(result){

           var datalist_proname_code ='';
             for(var i=0;i<result.data.length;i++){
               datalist_proname_code +='<option value="'+result.data[i].name+'"/>';
             }
            $("#productname").html(datalist_proname_code);
         });
       },

        //"产品确认"按钮事件
        product_name_commit_function:function(e){
        	//款式名单输入框输入框绘制
        	proname_submit_html();

        },

         //点击客户自动添加到当前客户
        add_current_customer_form_table:function(e){
            var self= this;
            var customer_id = e.currentTarget.attributes['id'].value;
            customer_id = customer_id.split('-')[1];
            batchModel.call('change_current_customer',["",customer_id,page_limit],{context: new instance.web.CompoundContext()}).then(function(result){
                if (result['code'] == 'failed'){
                    alert(result['message']);
                }else{
                    var customer = result.current_customer;
                    update_current_customer(self,customer);
                    leftmenu_prolist_html();
                    $("#customer-div").hide();
                    $("#add-model-btn").show();
                    $("#add-model").hide();
                }
            });
        },


       //搜索用户事件
        search_customer:function(e){
            var self = this;
            var key = e.currentTarget.value;
            batchModel.call('get_customter_list',[0,page_limit,key],{context: new instance.web.CompoundContext()}).then(function(customer_info_dict){
                update_customer_info_search(self,key);
                update_customer_info_table(self,customer_info_dict);
            });
        },
        //更换用户事件
        change_customer:function(e){
        	$("#left-menu").show();
        	$("#add-model").hide();
        	$("#edit-model").hide();
            var self = this;
            batchModel.call('get_customter_list',[0,page_limit,""],{context: new instance.web.CompoundContext()}).then(function(customer_info_dict){
                update_customer_info_search(self);
                update_customer_info_table(self,customer_info_dict);
            });
         },

         //“确认”按钮事件
         continue_order_function:function(e){
        	 $("#model_list_table_id").html("");
        	 var modle_list_table_html	='       <thead id="added-model-list-thead">'
														+'       </thead>'
														+'      <tbody id="added-model-list-html">'
														+'      </tbody>';
        	 $("#model_list_table_id").html(modle_list_table_html);
        	 var added_model_htmlcode ='';
        	 //获得款式ID
        	 var proid_num = parseInt($("#proid_number").text());
        	 //输出结果变量outdata_para
        	 var outdata_para={
        			 data:[],
        			 temp_id :null,
        	 };
        	 outdata_para.temp_id=proid_num;
        	 var attributes = $("select[id^=select_multi_id_]");
        	 if (attributes.length != 0){
        		 //每个款式有一条输入框
        		 var para =[];
        		 var paredata_list = [];
        		 for(var i=0;i<attributes.length;i++){
        			 para.push({'id':attributes[i].id.split("_")[3],data:[]});
        			 paredata_list.push({});
        			 //每个输入框的值
            		 var templist=[];
	        		 for(var j=0;j<attributes[i].selectedOptions.length;j++){
	        			 templist.push(attributes[i].selectedOptions[j].value);
	        		 }
	        		 paredata_list[i]=templist;
        		 }
        	 }
    		 for(var j=0;j<para.length;j++){
    			 para[j].data=paredata_list[j];
     		 }
    		 outdata_para.data=para;
    		 //输出对象outdata_para
        	 //console.log(outdata_para);

        	 //下方订单页弹出，可修改规格、数量
        	 $("#add_model_list").show();

        	 batchModel.call("get_product_products_filter",[outdata_para],{context: new instance.web.CompoundContext()}).then(function(result){
        		 if(result.code == "success"){
	        	    added_model_htmlcode ='';
	        	    var added_mode_theadcode='';
	        	    if(result.data.length!=0){
		        	    added_mode_theadcode	+='         <tr>'
										+'           <th><span id="all-check-text">全选</span> <input  id="allcheck-btn" name="Checkbox1" type="checkbox" style="margin:0;vertical-align:middle;"/></th>'
										+'           <th style="display:none;">商品编码</th>'
										+'           <th>产品名称</th>'
										+'           <th>材 质</th>'
										+'           <th>标准克重</th>'
										+'           <th>工 费(元/克)</th>'
										+'           <th>数 量(件)</th>'
										+'           <th>删 除</th>'
										+'        </tr>';
		        	    for(var i=0;i<result.data.length;i++){
			        	    added_model_htmlcode	+='        <tr  id="addedorder_tr_del_'+result.data[i].id+'">'
										+'          <td><input id="addedorder_check_'+result.data[i].id+'" name="order_checkbox" type="checkbox" class="check_model"/></td>'
										+'          <td style="display:none;"><input type="text" id="productid_'+result.data[i].id+'" list="productid" class="input130" value="'+result.data[i].id+'"></input></td>'
										+'           <td>'+result.data[i].name+'</td>'
										+'           <td>'+result.data[i].product_material+'</td>'
										+'          <td>'+result.data[i].standard_weight+'</td>'
										+'          <td>'+result.data[i].real_time_price_unit+'</td>'
										+'           <td width="160px"><button id="order-jian-'+result.data[i].id+'" class="btn btn-warning btn-sm ordernum-jian btn-temp">-</button><input type="text"  id="ordernum_'+result.data[i].id+'"  class="input70 ordernum_onchange" value="0"></input><button  id="order-add-'+result.data[i].id+'" class="btn btn-primary btn-sm ordernum-add btn-temp">+</button><span id="istf_'+result.data[i].id+'" style="display:none;">1000</span></td>'
										+'           <td><button id="del-'+result.data[i].id+'" type="button" class="btn btn-danger added-order-del-btn">X</button></td>'
										+'        </tr>';

		        	    }
		        	    $("#added-model-list-thead").html(added_mode_theadcode);
				        $("#added-model-list-html").html(added_model_htmlcode);
        	    	 }
        		 }else{
        	    		$("#added-model-list-html").html("");
        	    		$("#added-model-list-thead").html("没有查询到合适的产品");
        	    }
        	 });
        	 //公有“确认款式”的数量add_order_num
        	 add_order_num++
         },

         //“全选”按钮事件
         allcheck_function:function(e){
        	 var allcheck =$(".check_model");
        	 if(e.target.checked == false){
        		 allcheck.each(function(){this.checked=false;});
        		 $("#all-check-text").html("全选");
        	 }
        	 if(e.target.checked == true){
        		 allcheck.each(function(){this.checked=true;});
        		 $("#all-check-text").html("反选");
        	 }
         },

         //订单“提交”按钮
         order_submit_function:function(e){
        	 needSort=null;
         	var productid_num = $("input[id^=productid_]");
         	var ordernum_num = $("input[id^=ordernum_]");
         	var ordersubmit_list =[];
         	var ordersubmit_biglist ={};
         	for(var i=0;i<productid_num.length;i++){
         		var productid_code = productid_num[i].value;
         		var ordernum_code = ordernum_num[i].value;
         		var ordernum_code_num=0;
         		if(ordernum_code !="0"){
         			ordernum_code_num =parseInt(ordernum_code);
         			ordersubmit_list.push({'id':productid_code,'qty':ordernum_code_num});
         		}

         	}
         	//提交订单数据ordersubmit_list
         	ordersubmit_biglist.data=ordersubmit_list;
          if(ordersubmit_biglist.data.length != 0){
           	batchModel.call('add_product_to_order',[ordersubmit_biglist],{context: new instance.web.CompoundContext()}).then(function(result){
           		if(result.code=="success"){
           			leftmenu_prolist_html();
           			//返回添加款式，继续添加
           			model_load();
           		}
           	});
          }else{
            alert("未选择产品，提交不成功，请重新选择！");
          }
         },

         //已下订单款式"保存"按钮事件
         addorder_submit_function:function(e){
         	var productid_num = $("td[id^=added-proid-sum-]");
         	var ordernum_num = $("input[id^=ordernum_]");
         	var ordersubmit_list =[];
         	var ordersubmit_biglist ={};
         	for(var i=0;i<productid_num.length;i++){
         		var productid_code = productid_num[i].innerText;
         		var ordernum_code = ordernum_num[i].value;
         		var ordernum_code_num=0;
     			ordernum_code_num =parseInt(ordernum_code);
     			ordersubmit_list.push({'id':productid_code,'qty':ordernum_code_num});
         	}

         	//提交订单数据ordersubmit_list
         	ordersubmit_biglist.data=ordersubmit_list;
         	console.log(ordersubmit_biglist);

         	batchModel.call('add_product_to_order',[ordersubmit_biglist],{context: new instance.web.CompoundContext()}).then(function(result){
         		if(result.code=="success"){
         			//转到"定制下单页"继续下单
         			//model_load();
         		}
         	});
         },

         //产品列表的“删除”按钮
         added_order_del_function:function(e){
        	 var addedorder_del_id=(e.target.id).split("-")[1];
        	 $("#addedorder_tr_del_"+addedorder_del_id).remove();
         },

         //产品列表的"批量删除"按钮
         batch_del_btn_function:function(e){
	        	var addedorder_check_num = $("input[id^=addedorder_check_]");
	        	//获得多选框的产品ID
	        	var addedorder_alldel_id;
	        	var addedorder_alldel_checked_num = 0;
	        	for(var i=0;i<addedorder_check_num.length;i++){
		        	if(addedorder_check_num[i].checked){
		        		addedorder_alldel_checked_num++;
		        	}
	        	}
	        	console.log(addedorder_alldel_checked_num);
	        	if(addedorder_alldel_checked_num != 0){
		        	for(var i=0;i<addedorder_check_num.length;i++){
			        	if(addedorder_check_num[i].checked){
			        		addedorder_alldel_id=(addedorder_check_num[i].id).split("_")[2];
			        		$("#addedorder_tr_del_"+addedorder_alldel_id).remove();
			        	}
		        	}
		        	$("#all-check-text").html("全选");
		        	$("#allcheck-btn").attr("checked", false);
	        	}else{
	        		alert("你没有选择需要删除的产品，请重新选择！");
	        	}

         },

         //产品款式数量减1
         ordernum_jian_function:function(e){
        	 if(e.target.nextElementSibling.value>0){
        		 e.target.nextElementSibling.value--;
        		 //e.target.previousElementSibling.defaultValue =e.target.previousElementSibling.value;
        	 }
         },

         //产品款式数量加1
         ordernum_add_function:function(e){
        	 //console.log(e.currentTarget.parentNode.parentNode);

	       e.target.previousElementSibling.value++;
	    	 e.target.previousElementSibling.defaultValue =e.target.previousElementSibling.value;

        	var tr = e.currentTarget.parentNode.parentNode;

	    	 $("#addedorder_tr_del_"+(e.target.id).split("-")[2]).css('background-color','#fff3db');


//        	if (tr!=needSort && needSort !=null){
//        		console.log("需要排序");
//        		console.log(needSort);
//
//        		$("#added-model-list-html").before(needSort);
//        		$("#addedorder_tr_del_"+(e.target.id).split("-")[2]).css('background-color','#fff3db');
//
////	        	 var onchange_id="#istf_"+(e.target.id).split("-")[2];
////	        	 $(onchange_id).html("1");
////
////	        	 $("#addedorder_tr_del_"+(e.target.id).split("-")[2]).css('background-color','#fff3db');
////
////
////	    		 var addedorder_tr_del_html = $("tr[id^=addedorder_tr_del_]");
//////	    		 console.log(addedorder_tr_del_html[2].cells[6].childNodes[1].defaultValue);
////			    var arr = [];
////			    for(var i=0;i<addedorder_tr_del_html.length;i++){
////				    	arr.push(addedorder_tr_del_html[i]);
////			    }
////			    console.log(arr);
//
////			    //数组的排序JS
////			    //console.log(arr[0].cells[6].childNodes[3].innerText);
////			    arr.sort(function(a,b){return a.cells[6].childNodes[3].innerText - b.cells[6].childNodes[3].innerText});
////
////			    //console.log(arr);
////	    		 var order_add_htmlcode='';
////	    		 for(var j=0;j<arr.length;j++){
////	    			 order_add_htmlcode+=arr[j].outerHTML;
////	    		 }
////	    		 $("#added-model-list-html").html(order_add_htmlcode);
//        		needSort="";
//        		console.log("排序完成");
//        	}
//        	needSort = tr;
//        	console.log(needSort);
         },

         //数字输入框手动输入框
         ordernum_onchange_function:function(e){

        	 //数量输入框输入变化替换开始
	        	 var onchange_id="#istf_"+(e.target.id).split("_")[1];
	        	 $(onchange_id).html("1");
	        	 $("#addedorder_tr_del_"+(e.target.id).split("_")[1]).css('background-color','#fff3db');
	    		 var addedorder_tr_del_html = $("tr[id^=addedorder_tr_del_]");
			    var arr = [];
			    for(var i=0;i<addedorder_tr_del_html.length;i++)
			    {
			        arr.push(addedorder_tr_del_html[i]);
			    }
			    e.currentTarget.defaultValue = e.currentTarget.value;

			    //数组的排序JS
			    //console.log(arr[0].cells[6].childNodes[3].innerText);
			    //arr.sort(function(a,b){return a.cells[6].childNodes[3].innerText - b.cells[6].childNodes[3].innerText});

	    		 var order_add_htmlcode='';
	    		 for(var j=0;j<arr.length;j++){
	    			 order_add_htmlcode+=arr[j].outerHTML;
	    		 }
	    		 $("#added-model-list-html").html(order_add_htmlcode);
        	//数量输入框输入变化替换结束
         },

        //当前用户（业务员）的界面，
        display_current_user_info:function(self,current_user_info){
        	//console.log(current_user_info);
            var htmlValues = {
                'currentCustomer':current_user_info.current_customer,
            }
        	self.$el.append(QWeb.render("BatarBatchOrderTemplate",htmlValues));

           //console.log(current_user_info.current_customer);
	        if(current_user_info.current_customer){
	        	$("#customer-div").hide();
	        	$("#add-model-btn").show();
	        	$("#add-model").show();
	        }else{
	        	$("#customer-div").show();
	        	$("#add-model-btn").hide();
	        	$("#add-model").hide();
	        }


        	//左方"已下订单" 菜单添加
            leftmenu_prolist_html();
        	//右边"添加款式“内容添加
        	add_model_html();
        	$("#tempid").select2();
        },
    });
    instance.web.client_actions.add("batar_batch_order","instance.batar_batch_order.HomePage");
}


var LODOP; //声明为全局变量      
function PrintOneURL(strID){
	LODOP=getLodop();  
	//LODOP.PRINT_INIT("打印控件功能演示_Lodop功能_按网址打印");
//	LODOP.ADD_PRINT_URL(30,20,746,"95%",document.getElementById(strID).value);
	LODOP.ADD_PRINT_URL(30,20,746,"100%",'file:///E:/百泰集团/js素材/jquery二维码/2.html');
	LODOP.SET_PRINT_STYLEA(0,"HOrient",3);
	LODOP.SET_PRINT_STYLEA(0,"VOrient",3);

	LODOP.PREVIEW();			
};	
function PrintOneURL1(strID){
	LODOP=getLodop();  
	//LODOP.PRINT_INIT("打印控件功能演示_Lodop功能_按网址打印");
//	LODOP.ADD_PRINT_URL(30,20,746,"95%",document.getElementById(strID).value);
	LODOP.ADD_PRINT_URL(30,20,746,"100%",'file:///E:/百泰集团/js素材/jquery二维码/2.html');
	LODOP.SET_PRINT_STYLEA(0,"HOrient",3);
	LODOP.SET_PRINT_STYLEA(0,"VOrient",3);
	LODOP.PRINT();			
};	

