var Scatter = function(settings) {
	this.settings = settings
	this.data = this.settings.data
	this.defineFunctions()
	this.setScales()
	
	this.div = d3.select('#' + settings.container).append('div').attr('id', settings.id).attr('class', 'chart')
		.style('position', 'absolute')
		.style('top', this.settings.position.top + 'px')
		.style('left', this.settings.position.left + 'px')
		.style("width", this.settings.width  + 'px')
		.style("height", this.settings.height + 'px')
		
	this.title = this.div.append('div').attr('id', settings.id + '-title').style('width', this.settings.width + 'px').style('text-align', 'center').text('Topic ' + this.settings.topic + ' Proportions')
	this.build()
}


Scatter.prototype.defineFunctions = function() {
	var that = this
	
	that.legendRectFunc = function(leg) {
		leg.attr("width", that.settings.legend.rectWidth)
		   .attr("height", function(d) {
				return that.settings.legend.rectHeight
			})			
			.attr('fill', function(d) {
				return that.colorScale(d)
			})
			.attr('class', function(d) {
				return 'leg-rect'
			})
	}
	
	that.legendTextFunc = function(txt) {
		txt.text(function(d) {
			var limit = Math.floor((that.settings.margin.right -10)/10.5)
			var fullText =   d
			var text = fullText
			return text
		})
		.attr('fulltext', function(d) {  
			var fulltext =   d
			return fulltext
		})
		.attr('x', that.settings.legend.rectWidth + 5)
		.attr('y', that.settings.legend.rectHeight/2)
		.attr('fill', function(d) {
			var color =  'black'
			return color
		})
		.attr('class', function(d) {
			return 'leg-text'
		})
	}
	that.zoom = function() {
 		that.points.attr('transform', that.transform)
		that.xaxisLabels.call(that.xaxis)
		that.yaxisLabels.call(that.yaxis)
	}
	
	that.transform = function(d) {
	  return "translate(" + that.xScale(d.x) + "," + that.yScale(d.y) + ")";
	}
	
	that.pointFunction = function(point) {
		point
		.attr('transform', that.transform)
		.attr('r', function(d) {
			var radius =  d.id == that.settings.highlighted ? that.settings.highlightedRadius : that.settings.radius
			return radius
		})
		.attr('class', function(d) {
			var klass = d.id == that.settings.highlighted ? 'point highlighted' : 'point'
			return klass
		})
		.attr('fill', function(d) {
			console.log(d.colorValue)
			return that.colorScale((d.colorValue))
		})
		.attr('id', function(d) {return 'id_' + d.id})
	}
}

Scatter.prototype.setScales = function() {
	var that = this
	this.settings.legend.rectHeight = this.settings.height/(2*this.settings.colorLabels.length) >30 ? 30 : this.settings.height/(2*this.settings.colorLabels.length) 
	this.settings.radiusHighlighted = this.settings.radius * 3
	this.xScale = d3.scale.linear().domain(that.settings.domain.x).range([this.settings.highlightedRadius + this.settings.stroke, this.settings.width - this.settings.highlightedRadius -  this.settings.stroke - this.settings.margin.left - this.settings.margin.right])
	this.yScale = d3.scale.linear().domain(that.settings.domain.y).range([this.settings.highlightedRadius+ this.settings.stroke, this.settings.height - this.settings.highlightedRadius -  this.settings.stroke - this.settings.margin.top - this.settings.margin.bottom ])
	var colorDomain = d3.range(this.settings.domain.colors[1],this.settings.domain.colors[0], -(this.settings.domain.colors[1] - this.settings.domain.colors[0])/11)
	console.log('color variable type ', this.settings.colorVariableType == 'string')
	this.colorScale = this.settings.colorVariableType == "string" ? d3.scale.category10() : d3.scale.linear().domain(colorDomain).range(this.settings.colorRange)
	this.legendScale = d3.scale.linear()
		.domain(this.settings.domain.colors)
		.range([0,this.settings.legend.width]);
		
	this.xaxis = d3.svg.axis()
		.scale(that.xScale)
		.tickValues(that.settings.xVariableType == "string" ? that.settings.xLabels.map(function(d,i) {return i}) : null)
		.tickFormat(function(d) {
			return that.settings.xVariableType == "string" ? that.settings.xLabels[d] : d
		})
		.orient("bottom")
		
	this.yaxis = d3.svg.axis()
		.scale(that.yScale)
		.orient('left')	
}




Scatter.prototype.build = function() {
	var that = this
	this.wrapper = this.div.append("div")
		.attr('id', this.settings.id + '-svg-wrapper')
// 		.style('position', 'relative')
	.style('top', '0px')
		.style('left' ,'0px')
		
	this.xAxisSvg = this.wrapper.append('svg').attr('id', 'xaxis')
		.style('position', 'absolute')
		.style('top', (this.yScale.range()[1] + 25) + 'px')
		.style('left', this.settings.margin.left + 'px')
		.style('width', that.settings.width + 'px')
		.style('height', 80+ 'px')


	this.yAxisSvg = this.wrapper.append('svg').attr('id', 'yaxis').style('height', that.yScale.range()[1] + + that.settings.highlightedRadius + that.settings.stroke +'px')

	var left = $.browser.mozilla == true ? 0 : this.settings.margin.left
	this.pointsSvg = this.wrapper.append('svg')
		.attr('width', this.settings.width)
		.attr("height", this.yScale.range()[1] + that.settings.highlightedRadius+ that.settings.stroke )
		.attr('id', this.settings.id + '-svg')
		.style('position', 'absolute')
		.style('left', left + 'px')
		.attr("transform", "translate(" + this.settings.margin.left + "," +10+ ")")
		
	this.zoomG = this.pointsSvg.append("g")
    	.call(d3.behavior.zoom().x(that.xScale).y(that.yScale).scaleExtent([1, 8]).on("zoom", that.zoom));
	
	this.zoomRect = this.zoomG.append("rect")
		.attr("class", "overlay")
		.attr("width", this.xScale.range()[1])
		.attr("height", this.yScale.range()[1])

    
	this.g = this.pointsSvg.append("g")
		.attr('id', this.settings.id + '-g')
	
	this.points = this.g.selectAll('.point')
				.data(this.data, function(d) {return d.id})
				.enter().append('circle')
				.call(this.pointFunction)
			
		
	this.xaxisLabels = this.xAxisSvg.append("g")
					.attr("class", "axis xaxis")
					.attr("id", "xaxis-label")
					.call(this.xaxis)
					
	this.xtitleDiv = this.div.append('div')	.style('text-align', 'center')
					.style('margin-top', '10px')
					
	this.xtitleText = this.xtitleDiv.append('text')
					.text(this.settings.xtitle)
					.attr('id', 'xaxistext')
					.attr('class', 'axis-label')


	
				
	this.yaxisLabels = this.yAxisSvg.append('g')
						.attr('class', 'axis yaxis')
						.attr('id', 'yaxis-label')
						.attr('transform', 'translate(' + (this.settings.margin.left + 10) + ',0)')
						.call(this.yaxis)

						
	this.ytitle = this.yAxisSvg.append('text')
					.text(this.settings.ytitle)
					.attr('transform', 'translate(' + (30) + ',' + (this.settings.height/2 - 20)+ ') rotate(-90)')
					.attr('id', 'yaxistext')
					.attr('class', 'axis-label')

		
	this.moveHighlighted()	
	if(this.settings.colorVariableType == 'integer') this.buildContinuousLegend()	
	else this.buildCategoricalLegend() 	
	this.addHover()
}
	
Scatter.prototype.buildContinuousLegend = function() {
	var that = this
	that.legendWrapper = that.div.append('div').attr('id', that.settings.id + '-legend-wrapper').style('pointer-events', 'none')
	that.legendDiv = that.legendWrapper.append('div').attr('id', that.settings.id + '-legend-div').style('position', 'absolute').style('top', (this.settings.height - this.settings.margin.bottom) + 'px')
	that.legend = that.legendDiv
		.append("svg")		
		.attr('id', that.settings.id + '-legend-svg')
		.attr("height", that.settings.legend.height + 40)
		.attr("width", that.settings.legend.width + that.settings.legend.shift + 24)
	
	that.gradient = that.legend
		.append("svg:defs")
			.append("svg:linearGradient")
			.attr("id", "map-gradient")
			.attr("x1", "0%")
			.attr("y1", "0%")
			.attr("x2", "100%")
			.attr("y2", "0%");
			
	$.extend([],that.settings.colorRange).reverse().forEach(function(d,i){
			that.gradient.append("svg:stop")
				.attr("offset",((i+1)/(12)))
				.attr("stop-color", d)
				.attr('id', 'stop-color-' + i)
		});
		
	that.legendBar = that.legend.append("g")
			.attr('transform', 'translate(' + that.settings.legend.shift+',0)')
			.append('rect').attr('id', that.settings.id + '-legendrect')
			.attr('y', '0px')
			.attr('x', '0px')
			.attr('height', that.settings.legend.height)
			.attr('width',  that.settings.legend.width)
			.attr('stroke', 'none')
			.attr('fill', 'url(#map-gradient)')


	that.legendAxes = d3.svg.axis()
		.scale(that.legendScale)
		.orient('bottom')
	
	that.legendLabels = that.legend.append('g')
		.attr('transform', 'translate(' + that.settings.legend.shift+ ',' + (that.settings.legend.height) + ')')
		.attr('class', 'axis')
		.call(that.legendAxes);
		
	that.legendText = that.legend.append('g')
		.attr('transform', 'translate(' + (that.settings.legend.shift -40)+ ',' + (that.settings.legend.height/2) + ')')
		.append('text').text(this.settings.legendTitle)

}

Scatter.prototype.moveHighlighted = function() {
	var select = $("#id_" + this.settings.highlighted)[0]
	select.parentNode.appendChild(select)
}

Scatter.prototype.updateHighlighted = function(hl) {
	this.settings.highlighted = hl
	d3.selectAll('.highlighted').attr('class', 'point').attr('r', this.settings.radius)
	d3.select('#id_'  + hl).attr('class', 'point highlighted').attr('r', this.settings.highlightedRadius)
	this.moveHighlighted()			

}

Scatter.prototype.updatePosition = function(settings) {
	var that = this
	this.settings = settings
	this.div
		.style('position', 'relative')
		.style('top', this.settings.position.top + 'px')
		.style('left', this.settings.position.left + 'px')
		.style("width", this.settings.width  + 'px')
		.style("height", this.settings.height + 'px')
		
	this.title.style('width', this.settings.width + 'px')
	d3.select('#' + settings.id + '-title').text('Topic ' + this.settings.topic + ' Proportions')
	this.data = settings.data
	this.setScales()
	this.ytitle.attr('transform', 'translate(' + (30) + ',' + (this.settings.height/2)+ ') rotate(-90)')
	this.zoomRect.attr("width", this.xScale.range()[1])
		.attr("height", this.yScale.range()[1])
		
	this.pointsSvg
		.attr("width", this.settings.width)
		.attr("height", this.yScale.range()[1] + that.settings.highlightedRadius+ that.settings.stroke )
		
	this.xAxisSvg.transition().duration(500).style('top', (this.yScale.range()[1] + 25) + 'px')
		.style('left', this.settings.margin.left + 'px')
		.style('width', that.settings.width + 'px')

	this.yAxisSvg.style('height', that.yScale.range()[1] + + that.settings.highlightedRadius + that.settings.stroke +'px')
	this.xaxisLabels.transition().duration(500).call(this.xaxis)
	this.yaxisLabels.transition().duration(500).call(this.yaxis)
 	this.pointsSvg.selectAll('.point').data(this.data, function(d) {return (d.id)}).transition().duration(500).call(this.pointFunction)	
	this.xtitleText.text(this.settings.xtitle)
	
	setTimeout(function() {
		that.zoomG.call(d3.behavior.zoom().x(that.xScale).y(that.yScale).scaleExtent([1, 8]).on("zoom", that.zoom));
	}, 700)
	$('#' + this.settings.id + '-legend-wrapper').remove()
	if(this.settings.colorVariableType == 'integer') this.buildContinuousLegend()	
	else this.buildCategoricalLegend() 	


}


Scatter.prototype.buildCategoricalLegend = function(parent, id) {
	var that = this
	var x =  that.xScale.range()[1]
	var y = 10
	legendData = that.settings.colorLabels
	if(legendData.length == 1) return
	var labelScale = d3.scale.linear().domain([legendData.length-1,0]).range([0,(that.settings.height - 50)]) 
		
	var legend = this.pointsSvg.append('g').attr('id', this.settings.id + '-legend-wrapper').attr('transform', 'translate(' + (x) + ',' +(y) + ')').style('cursor', 'pointer')
	var labels = legend.selectAll('g')
					.data(legendData, function(d) {return d})
					.enter().append('g')
					.attr('class', 'legend-g')
					.attr('transform', function(d,i) {return 'translate(0,' +((i*40) ) + ')' })
					
	var legRects = labels.append('rect').call(that.legendRectFunc)
		

	var text = labels.append('text').call(that.legendTextFunc)
	$('.legend-g').poshytip({
		slide: false, 
		followCursor: true, 
		alignTo: 'cursor', 
		showTimeout: 0, 
		liveevents:true,
		hideTimeout: 0, 
		alignX: 'center', 
		alignY: 'inner-bottom', 
		className: 'tip',
		offsetY: 10,
		content: function(a,tip){
			var text = this.__data__
			return text
		}
	})			
}


Scatter.prototype.setOpacity  = function(opacity) {
	this.g.selectAll('.point').style('opacity', opacity)
}

Scatter.prototype.setRadius  = function(radius) {
	this.g.selectAll('.point').transition().duration(500).attr('r', radius)
}

Scatter.prototype.addHover = function() {
	var that = this
	$('.point').poshytip({
		slide: false, 
		followCursor: true, 
		alignTo: 'cursor', 
		showTimeout: 0, 
		liveevents:true,
		hideTimeout: 0, 
		alignX: 'center', 
		alignY: 'inner-bottom', 
		className: 'tip',
		offsetY: 10,
		content: function(a,tip){
			var d = this.__data__
			var formatter = d3.format('.2s')
			var text = '<b>ID: </b>' + d.id + '</br>'
			text += '<b>' + that.settings.ytitle + ': </b> ' + formatter(d.y) + '</br>'
			text += '<b>' + that.settings.xtitle + ': </b> ' + that.settings.xLabels[d.x]
			return text
		}
	})
	
	

}
