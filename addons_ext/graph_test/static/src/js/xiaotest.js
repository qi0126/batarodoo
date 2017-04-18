//openerp.graph_test = function(instance, local){
//    var _t = instance.web._t,
//        _lt = instance.web._lt;
//    var QWeb = instance.web.qweb;
//
////    local.Homepage = instance.Widget.extend({
////        className: 'oe_xiao_tes',
////        start: function(){
////            var products = new local.ProductWidget(
////                this, ['apple', 'au', 'ag', 'iphone']);
////            products.appendTo(this.$el);
////        }
////    })
////
////    local.ProductWidget = instance.Widget.extend({
////        template: 'Xiaotest',
////        init: function(parent, products){
////            this._super(parent);
////            this.products = products;
////            }
////        })
////    local.ColorInputWidget = instance.Widget.extend({
////        template: "ColorInputWidget",
////        events: {
////            'change input': 'input_changed'
////        },
////        start: function() {
////            this.input_changed();
////            return this._super();
////        },
////        input_changed: function() {
////            var color = [
////                "#",
////                this.$(".oe_color_red").val(),
////                this.$(".oe_color_green").val(),
////                this.$(".oe_color_blue").val()
////            ].join('');
////            this.set("color", color);
////        },
////    });
////
////    local.HomePage = instance.Widget.extend({
////        template: "HomePage",
////        start: function() {
////            this.colorInput = new local.ColorInputWidget(this);
////            this.colorInput.on("change:color", this, this.color_changed);
////            return this.colorInput.appendTo(this.$el);
////        },
////        color_changed: function() {
////            this.$(".oe_color_div").css("background-color", this.colorInput.get("color"));
////        },
////    });
//    local.HomePage = instance.web.Widget.extend({
//        template: 'HomePage',
//        start: function(){
//            return new local.Price(this).appendTo(this.$el);},
//        });
//    local.Price = instance.web.Widget.extend({
//        template: 'Price',
//        start: function(){
//            var self = this;
//            return new instance.web.Model('xiao.test.graph')
//                .query(['name'])
//                .order_by('-create_date', '-id')
//                .first()
//                .then(function(result){
//                    self.$('.oe_test_price').text(result.name);
//                });
//            },
//        })
//    instance.web.client_actions.add('xiaotest.page', 'instance.graph_test.HomePage');
//    }
//
openerp.graph_test = function(instance, local){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.ProductAttibutePage = instance.web.Widget.extend({
        template: 'ProductAttibutePice',
        start: function(){

            var chart;
            var data;
            var model = new instance.web.Model('xiao.test.graph');

            var randomizeFillOpacity = function() {
                var rand = Math.random(0,1);
                for (var i = 0; i < 100; i++) { // modify sine amplitude
                    data[4].values[i].y = Math.sin(i/(5 + rand)) * .4 * rand - .25;
                }
                data[4].fillOpacity = rand;
                chart.update();
            };
//            model.call('get_bi_data', {context: new instance.web.CompoundContext()}).then(function(result){
//            model.call('get_bi_data', {context: new instance.web.CompoundContext()})
            nv.addGraph(function() {
                chart = nv.models.lineChart()
                    .options({
                        transitionDuration: 300,
                        useInteractiveGuideline: true
                    })
                ;
                // chart sub-models (ie. xAxis, yAxis, etc) when accessed directly, return themselves, not the parent chart, so need to chain separately
                chart.xAxis
                    .axisLabel("Time (s)")
//                    .tickFormat(d3.format(',.1f'))
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

                data = sinAndCos();
//                data = get_data();
                d3.select('#chart1').append('svg')
                    .datum(data)
//                    .datum(result)
                    .call(chart);
                nv.utils.windowResize(chart.update);
                return chart;
            });
//            })
//            function get_data(){
//                return model.call('get_bi_data', {context: new instance.web.CompoundContext()})
//            }
            function sinAndCos() {
                var sin = [],
                    sin2 = [],
                    cos = [],
                    rand = [],
                    rand2 = []
                    ;
                for (var i = 0; i < 100; i++) {
                    sin.push({x: i, y: i % 10 == 5 ? null : Math.sin(i/10) }); //the nulls are to show how defined works
                    sin2.push({x: i, y: Math.sin(i/5) * 0.4 - 0.25});
                    cos.push({x: i, y: .5 * Math.cos(i/10)});
                    rand.push({x:i, y: Math.random() / 10});
                    rand2.push({x: i, y: Math.cos(i/10) + Math.random() / 10 })
                }
                return [
//
//                    {
//                        area: true,
//                        values: sin,
//                        key: "Sine Wave",
//                        color: "#ff7f0e",
//                        strokeWidth: 4,
//                        classed: 'dashed'
//                    },
//                    {
//                        values: cos,
//                        key: "Cosine Wave",
//                        color: "#2ca02c"
//                    },
//                    {
//                        values: rand,
//                        key: "Random Points",
//                        color: "#2222ff"
//                    },
                    {
                        values: rand2,
                        key: "Random Cosine",
                        color: "#667711",
                        strokeWidth: 3.5
                    },
//                    {
//                        area: true,
//                        values: sin2,
//                        key: "Fill opacity",
//                        color: "#EF9CFB",
//                        fillOpacity: .1
//                    }
                ];
            }
        }
     })
//        start: function(){
//            return new local.Price(this).appendTo(this.$el);},
//        });
//    local.Price = instance.web.Widget.extend({
//        template: 'Price',
//        start: function(){
//            var self = this;
//            return new instance.web.Model('xiao.test.graph')
//                .query(['name'])
//                .order_by('-create_date', '-id')
//                .first()
//                .then(function(result){
//                    self.$('.oe_test_price').text(result.name);
//                });
//            },
//        });
    instance.web.client_actions.add('xiaotest.page', 'instance.graph_test.ProductAttibutePage');
}