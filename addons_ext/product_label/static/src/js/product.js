$(".default-code").change(function(){
	console.log(123213123123123);
	$("#bcTarget").empty().barcode($(".default-code").text(),"code128",{barWidth:1, barHeight:30,showHRI:false});
});
console.log(123123123123);