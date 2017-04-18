openerp.batar_bi = function(instance, local){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.ProductAttibutePage = instance.web.Widget.extend({
        template: 'ProductAttibutePice',
        start: function(){

            var chart;
            var data;
            var model = new instance.web.Model('batar.bi');
            model.call('get_product_bi_data', {context: new instance.web.CompoundContext()}).then(function(result){
//            var model = new instance.web.Model('xiao.test.graph');
//            model.call('get_bi_data', {context: new instance.web.CompoundContext()}).then(function(result){
                nv.addGraph(function() {
                    chart = nv.models.lineChart()
                        .options({
                            transitionDuration: 300,
                            color: d3.scale.category10().range(),
                            useInteractiveGuideline: true

                        })
                    ;
                    // chart sub-models (ie. xAxis, yAxis, etc) when accessed directly, return themselves, not the parent chart, so need to chain separately



                    chart.xAxis
                        .axisLabel("Time (s)")
                        .tickFormat(function(d) { return d3.time.format("%x %X")(new Date(d)); })
                        .tickValues([1451606400000,1483228799000])
//                        .tickValues([])
//                        .tickFormat(d3.time.format(',.1f'))
                        .staggerLabels(true)
                    ;
                    chart.yAxis
                        .axisLabel('Price (￥)')
                        .tickFormat(function(d) {
                            if (d == null) {
                                return 'N/A';
                            }
                            return d3.format(',.2f')(d);
                        })
                    ;
                    d3.select('#chart1').append('svg')
                        .datum(result)
                        .call(chart);
                    nv.utils.windowResize(chart.update);
                    return chart;
                });
            })
        }
    })
    instance.web.client_actions.add('product_attribute.page', 'instance.batar_bi.ProductAttibutePage');
}