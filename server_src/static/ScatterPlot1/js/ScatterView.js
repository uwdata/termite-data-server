var ScatterView = Backbone.View.extend({
	el:'#main',
	defaults:{
		chart:{
			width:600, 
			height:400, 
			margin:{
				left:100, 
				right:120, 
				top:100, 
				bottom:0
			}, 
			radius:5,
			highlightedRadius:10, 
			stroke:1,
			xtitle:'Day of the Year', 
			ytitle:'Proportion'
		}, 
		textbox:{
			width:400, 
			height:400, 	
		
		}
	},
	initialize:function(options) {
		this.options = _.extend({}, this.defaults, options)
		this.sizeView()
		this.prepData()
		this.getChartLimits()
		this.model.on('change:highlighted', function() {
			this.chart.updateHighlighted(this.model.get('highlighted'))
		}, this)
		this.model.on('change:topic', function() {
			this.model.prep()
			this.prepData()
			this.getChartLimits()
			this.chart.updatePosition(this.loadSettings())
		}, this)
		this.model.on('change:xVariable change:colorVariable', function() {
			this.model.prep()
			this.sizeView()
			this.prepData()
			this.getChartLimits()
			this.chart.updatePosition(this.loadSettings())
		}, this)
		this.model.on('change:opacity', function() {
			var opacity = this.model.get('opacity')
			this.chart.setOpacity(opacity)
		}, this)
		
		this.model.on('change:radius', function() {
			var radius = this.model.get('radius')
			this.chart.setRadius(radius)
		}, this)
		
		this.render()
	},
	prepData:function() {
		var that = this
		this.chartData = []
		this.model.data.map(function(d,i) {
			var color =  'blue'
			that.chartData.push({
				id:d.id, 
				x:isFinite(d.xValue) ? Number(d.xValue) : d.xValue, 
				colorValue:d.colorValue,
				y:Number(d.proportion), 
				color:color
			})
		})	
	},
	
	getChartLimits:function() {
		this.domain = {
			x:null,
			y:null,
		}
		var xValues= this.chartData.map(function(d){return d.x})
		var colorValues= this.chartData.map(function(d){return d.colorValue})
		var yValues= this.chartData.map(function(d){return d.y})
		this.domain.x = this.model.get('xVariableType') == 'integer' ? [d3.min(xValues), d3.max(xValues)] : [-1,d3.set(xValues).values().length ]
		this.domain.colors = this.model.get('colorVariableType') == 'string' ? colorValues : [d3.min(colorValues), d3.max(colorValues)]
		this.domain.y = [d3.max(yValues), d3.min(yValues)]
		
// 		{min:this.min, max:this.max}
	}, 
	
	render:function() {
		var that = this
		this.chart = new Scatter(that.loadSettings());
		
	this.chart.g.selectAll(".point")
			.on("click", function(d){
				var doc_id = d.id;
				this.model.trigger("clickCircle", doc_id);
			}.bind(this) );

	}
})

ScatterView.prototype.sizeView = function() {
	var that = this
	that.options.chart.width = $(window).width()*2/3
	that.options.chart.height = $(window).height() - $('#top-controls').height() - 10
	that.options.chart.margin.bottom = this.model.get('colorVariableType') == 'string' | this.model.get('colorVariableType') == '' ? 0 : 100
	that.options.chart.margin.right = this.model.get('colorVariableType') == 'string' ? 120 : 0
	that.options.chart.position = this.options.chart.position == undefined ? {} : this.options.chart.position
	that.options.chart.position.top = $('#top-controls').height() + 10
	that.options.chart.position.left = 0
}

ScatterView.prototype.loadSettings = function() {
	var that = this
	return {
			id:this.options.chartid,
			domain:this.domain,
			container:that.el.id, 
			topic:Number(this.model.get('topic')) + 1,
			data:this.chartData, 
			width:this.options.chart.width, 
			height:this.options.chart.height, 
			margin:this.options.chart.margin,
			position:this.options.chart.position,
			xLabels:this.model.xLabels,
			colorLabels:this.model.colorLabels,
			colorRange:colorbrewer['RdYlBu'][11],
			xVariableType:this.model.get('xVariableType'),
			colorVariableType:this.model.get('colorVariableType'),
			radius:this.options.chart.radius,
			highlightedRadius:this.options.chart.highlightedRadius,
			stroke:this.options.chart.stroke,
			xtitle:this.model.get('xVariable'), 
			legendTitle:this.model.get('colorVariable'), 
			ytitle:this.options.chart.ytitle, 
			highlighted:this.model.get('highlighted'), 
			legend:{
				height:40, 
				width:this.options.chart.width*2/3, 
				shift:this.options.chart.margin.left,
				rectWidth:20, 
			
			}
		}
	

}
