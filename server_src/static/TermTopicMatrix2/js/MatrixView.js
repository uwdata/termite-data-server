/**
 * @class MatrixView
 * @classdesc MatrixView generates a matrix visualization.
 * By default, the visualization will created inside the first HTML element identified by the "div.MatrixView" tag.
 * Visual attributes (layout, sizes, and colors) are automatically recalculated to reflect changes in visibility, ordering, selection, highlighting, and labels.
 *
 * @author Jason Chuang <jcchuang@cs.stanford.edu>
 * @param {Object} options The "options" object must contain an entry "options.model" of type "MatrixModel".
 **/
var MatrixView = MatrixInteractions.extend({
	el : "div.MatrixView"
});

/**
 * Backbone-specific initialization routine.
 * @private
 **/
MatrixView.prototype.initialize = function( options ) {
	MatrixInteractions.prototype.initialize.call( this, options );
	this.__defineHtmlElements();
	this.__initModelEvents();
};

//==================================================================================================

MatrixView.prototype.CONST = _.extend( _.clone( MatrixInteractions.prototype.CONST ), {
	LEFT_PANEL_WIDTH : 90, // 125,
	TOP_PANEL_HEIGHT : 70, // 90,
	RIGHT_PANEL_WIDTH : 100,
	BOTTOM_PANEL_HEIGHT : 100,
	BOTTOM_BAR_MAX_LENGTH : 75,  // BOTTOM_PANEL_HEIGHT - 5
	FAR_PANEL_WIDTH : 125,
	FAR_BAR_MAX_LENGTH : 120,    // FAR_PANEL_WIDTH - 5

	LEFT_PADDING : 8, // 10,
	TOP_PADDING : 8, // 10,
	RIGHT_PADDING : 5,
	BOTTOM_PADDING : 5,
	FAR_PADDING : 8, // 10,
	OUTER_PADDING : 20,
	
	EXPANSION_SPACING : 210,
	EXPANSION_OFFSET : 30,
	EXPANSION_WIDTH : 135,

	MAX_RADIUS_PX : 20, // 24,
	SPACING_PX : 13.5, // 16,
	BAR_WIDTH_PX : 10.5, //12,          // SPACING_PX * 0.75
	TOP_LABEL_ANGLE_DEG : -65
});

//==================================================================================================

MatrixView.prototype.__initModelEvents = function() {
	this.__isRendering = false;
	this.__pendingModelEvents = {};
	this.__currentModelEvents = {};
	this.__ongoingModelEvents = {};
	this.__rescheduleViewRendering = _.debounce( this.__scheduleViewRendering, 20 );
	this.listenTo( this.model, "dirty", this.__onModelEvents );
};

MatrixView.prototype.__onModelEvents = function( dirty ) {
	this.__pendingModelEvents = this.__combineDirty__( this.__pendingModelEvents, dirty );
	this.__scheduleViewRendering();
};

MatrixView.prototype.__scheduleViewRendering = function() {
	if ( this.__isRendering )
		this.__rescheduleViewRendering();
	this.__isRendering = true;
	this.__currentModelEvents = this.__pendingModelEvents;
	this.__pendingModelEvents = {};
	this.__currentModelEvents = this.__combineDirty__( this.__currentModelEvents, this.__ongoingModelEvents );
	this.__ongoingModelEvents = {};
	this.__renderView();
	this.triggerDirty();
	this.__clearModelEvents();
	this.__isRendering = false;
};

MatrixView.prototype.__isDirtyModel = function() {
	var keys = Array.prototype.slice.call( arguments );
	return this.__isDirty__( this.__currentModelEvents, keys, 0 );
};

MatrixView.prototype.__getDirtyModel = function() {
	var keys = Array.prototype.slice.call( arguments );
	return this.__getDirty__( this.__currentModelEvents, keys, 0 );
};

MatrixView.prototype.__clearModelEvents = function() {
	this.__ongoingModelEvents = this.__combineDirty__( this.__ongoingModelEvents, this.__currentModelEvents );
	var duration = this.model.get( "vis:schedules" ).duration;
	d3.timer( function() {
		this.__ongoingModelEvents = {};
		return true;
	}.bind(this), duration );
};

//==================================================================================================

MatrixView.prototype.__renderView = function() {
	this.__calculateChartWidthAndColumnLayouts();
	this.__calculateChartHeightAndRowLayouts();
	this.__calculateSizes();
	this.__calculateDimensions();

	this.__resetElements();
	this.__renderElements();
	this.__resizeLayers();
	this.__resizeContainerAndDepths();
};

//==================================================================================================

MatrixView.prototype.__defineHtmlElements = function() {
	this.__selections = [];
	this.__scales = {};
	this.__defineContainerAndDepths();
	this.__defineLayers();
	this.__defineElements();
};

MatrixView.prototype.__defineContainerAndDepths = function() {
	// Apply class-based CSS rules
	this.$el.addClass( "MatrixView" );
	
	// Top-level containers
	this.__container = d3.select( this.el ).append( "div" ).attr( "class", "container" );
	this.__canvas = this.__container.append( "div" ).attr( "class", "canvas" );
	
	// Top-level keystroke listener
//	d3.select( "body" ).call( this.keystrokeListeners.bind(this) )

	// Back-to-front rendering
	this.__depths = {}
	this.__depths.catcher = this.__canvas.append( "div" ).attr( "class", "catcherLayer" ).attr( "z-index", -20 );
	this.__depths.svg = this.__canvas.append( "svg:svg" ).attr( "class", "svgLayer" ).attr( "z-index", -10 );
	this.__depths.html = this.__canvas.append( "div" ).attr( "class", "htmlLayer" ).attr( "z-index", 0 );
	this.__depths.overlay = this.__canvas.append( "svg:svg" ).attr( "class", "overlayLayer" ).attr( "z-index", 10 );
};

MatrixView.prototype.__defineLayers = function() {
	this.__layers = {};
	this.__layers.centerCatcher = {
		"content" : this.__depths.catcher.append( "div" ).attr( "class", "centerCatcher" ),
		"dims" : centerPanelDims,
		"renderer" : divRenderer
	};
	this.__layers.centerGrids = {
		"content" : this.__depths.svg.append( "svg:g" ).attr( "class", "centerGrids" ),
		"dims" : centerPanelDims,
		"renderer" : svgRenderer
	};
	this.__layers.centerControls = {
		"content" : this.__depths.html.append( "div" ).attr( "class", "centerControls" ),
		"dims" : centerPanelDims,
		"renderer" : divRenderer
	};
	this.__layers.centerPanel = {
		"content" : this.__depths.overlay.append( "svg:g" ).attr( "class", "centerPanel" ),
		"dims" : centerPanelDims,
		"renderer" : svgRenderer
	};
	this.__layers.leftPanel = {
		"content" : this.__depths.html.append( "div" ).attr( "class", "leftPanel" ),
		"dims" : leftPanelDims,
		"renderer" : divRenderer
	};
	this.__layers.topCatcher = {
		"content" : this.__depths.catcher.append( "div" ).attr( "class", "topPanel" ),
		"dims" : topPanelDims,
		"renderer" : divRenderer
	};
	this.__layers.topPanel = {
		"content" : this.__depths.html.append( "div" ).attr( "class", "topPanel" ),
		"dims" : topPanelDims,
		"renderer" : divRenderer
	};
	this.__layers.rightPanel = {
		"content" : this.__depths.html.append( "div" ).attr( "class", "rightPanel" ),
		"dims" : rightPanelDims,
		"renderer" : divRenderer
	};
	this.__layers.bottomPanel = {
		"content" : this.__depths.svg.append( "svg:g" ).attr( "class", "bottomPanel" ),
		"dims" : bottomPanelDims,
		"renderer" : svgRenderer
	};
	this.__layers.farPanel = {
		"content" : this.__depths.svg.append( "svg:g" ).attr( "class", "farPanel" ),
		"dims" : farPanelDims,
		"renderer" : svgRenderer
	};
	
	function centerPanelDims( chartWidth, chartHeight ) {
		return {
			"width" : chartWidth,
			"height" : chartHeight,
			"x" : this.CONST.OUTER_PADDING + this.CONST.LEFT_PANEL_WIDTH + this.CONST.LEFT_PADDING,
			"y" : this.CONST.OUTER_PADDING + this.CONST.TOP_PANEL_HEIGHT + this.CONST.TOP_PADDING
		};
	}
	function leftPanelDims( chartWidth, chartHeight ) {
		return {
			"width" : this.CONST.LEFT_PANEL_WIDTH,
			"height" : chartHeight,
			"x" : this.CONST.OUTER_PADDING,
			"y" : this.CONST.OUTER_PADDING + this.CONST.TOP_PANEL_HEIGHT + this.CONST.TOP_PADDING
		}
	}
	function topPanelDims( chartWidth, chartHeight ) {
		return {
			"width" : chartWidth,
			"height" : this.CONST.TOP_PANEL_HEIGHT,
			"x" : this.CONST.OUTER_PADDING + this.CONST.LEFT_PANEL_WIDTH + this.CONST.LEFT_PADDING,
			"y" : this.CONST.OUTER_PADDING
		};
	}
	function rightPanelDims( chartWidth, chartHeight ) {
		return {
			"width" : this.CONST.RIGHT_PANEL_WIDTH,
			"height" : chartHeight,
			"x" : this.CONST.OUTER_PADDING + this.CONST.LEFT_PANEL_WIDTH + this.CONST.LEFT_PADDING + chartWidth + this.CONST.RIGHT_PADDING,
			"y" : this.CONST.OUTER_PADDING + this.CONST.TOP_PANEL_HEIGHT + this.CONST.TOP_PADDING
		};
	}
	function bottomPanelDims( chartWidth, chartHeight ) {
		return {
			"width" : chartWidth,
			"height" : this.CONST.BOTTOM_PANEL_HEIGHT,
			"x" : this.CONST.OUTER_PADDING + this.CONST.LEFT_PANEL_WIDTH + this.CONST.LEFT_PADDING,
			"y" : this.CONST.OUTER_PADDING + this.CONST.TOP_PANEL_HEIGHT + this.CONST.TOP_PADDING + chartHeight + this.CONST.BOTTOM_PADDING
		};
	}
	function farPanelDims( chartWidth, chartHeight ) {
		return {
			"width" : this.CONST.FAR_PANEL_WIDTH,
			"height" : chartHeight,
			"x" : this.CONST.OUTER_PADDING + this.CONST.LEFT_PANEL_WIDTH + this.CONST.LEFT_PADDING + chartWidth + this.CONST.RIGHT_PADDING + this.CONST.RIGHT_PANEL_WIDTH + this.CONST.FAR_PADDING,
			"y" : this.CONST.OUTER_PADDING + this.CONST.TOP_PANEL_HEIGHT + this.CONST.TOP_PADDING
		};
	}
	function divRenderer( e, dims ) {
		e.style( "left", dims.x + "px" )
		 .style( "top", dims.y + "px" )
		 .style( "width", dims.width + "px" )
		 .style( "height", dims.height + "px" );
	}
	function svgRenderer( e, dims ) {
		e.attr( "transform", "translate(" +dims.x+ "," +dims.y+ ")" )
		 .attr( "width", dims.width )
		 .attr( "height", dims.height );
	}
};

MatrixView.prototype.__defineElements = function() {
	
	this.__elements = [];

	// Gridline elements:  x, y, circles, y-catcher
	var xGridline = function( d ) { 
		return this.__scales.xSpatial( d.columnPosition + 0.5 );
	}.bind(this);
	var yGridline = function( d ) { 
		return this.__scales.ySpatial( d.rowPosition + 0.5 );
	}.bind(this);
	var widthGridline = function( d ) {
		return this.__scales.xSpatial( d.columnPosition + 1 ) - this.__scales.xSpatial( d.columnPosition );
	}.bind(this);
	var xConstGridline = function( value ) { 
		var f = function() {
			return this.__scales.xSpatial( value > 0 ? value : this.__scales.columnDims + value );
		}.bind(this);
		return f;
	}.bind(this);
	var yConstGridline = function( value ) { 
		var f = function() {
			return this.__scales.ySpatial( value > 0 ? value : this.__scales.rowDims + value );
		}.bind(this);
		return f;
	}.bind(this);
	this.__elements.push({
		"identifier" : "div.yCatcher",
		"layer" : this.__layers.centerCatcher,
		"dataID" : "transitionColumnElements",
		"renderers" : {
			"initRenderer" : function(e) {
				e.style( "top", "0px" )
			},
			"updateAnimations" : function(e) {
				e.style( "left", xGridline )
				 .style( "width", widthGridline )
				 .style( "height", this.__scales.chartHeight + "px" )
			},
			"mouse" : this.mouseListeners
		}
	});
	this.__elements.push({
		"identifier" : "line.xGridlines",
		"layer" : this.__layers.centerGrids,
		"dataID" : "transitionRowElements",
		"renderers" : {
			"updateAnimations" : function(e) {
				e.attr( "x1", xConstGridline( 0.5 ) )
				 .attr( "x2", xConstGridline( -0.5 ) )
				 .attr( "y1", yGridline )
				 .attr( "y2", yGridline )
				 .style( "stroke", this.__getBackgroundColor.bind(this) )
				 .style( "stroke-width", this.__getGridlineStrokeWidth.bind(this) )
				 .style( "stroke-opacity", this.__getGridlineStrokeOpacity.bind(this) )
			}
		}
	});
	this.__elements.push({
		"identifier" : "line.yGridlines",
		"layer" : this.__layers.centerGrids,
		"dataID" : "transitionColumnElements",
		"renderers" : {
			"updateAnimations" : function(e) {
				e.attr( "x1", xGridline )
				 .attr( "x2", xGridline )
				 .attr( "y1", yConstGridline( 0.5 ) )
				 .attr( "y2", yConstGridline( -0.5 ) )
				 .style( "stroke", this.__getBackgroundColor.bind(this) )
				 .style( "stroke-width", this.__getGridlineStrokeWidth.bind(this) )
				 .style( "stroke-opacity", this.__getGridlineStrokeOpacity.bind(this) )
			}
		}
	});
	this.__elements.push({
		"identifier" : "circle.entries",
		"layer" : this.__layers.centerPanel,
		"dataID" : "transitionEntries",
		"renderers" : {
			"updateAnimations" : function(e) {
				e.attr( "cx", xGridline )
				 .attr( "cy", yGridline )
				 .attr( "r", function(d) { return this.__scales.rSize(d.value) }.bind(this) )
				 .style( "stroke", this.__getForegroundColor.bind(this) )
				 .style( "stroke-width", this.__getCircleStrokeWidth.bind(this) )
				 .style( "stroke-opacity", this.__getCircleStrokeOpacity.bind(this) )
				 .style( "fill", this.__getForegroundColor.bind(this) )
				 .style( "fill-opacity", this.__getCircleFillOpacity.bind(this) )
			},
			"mouse" : this.mouseListeners
		}
	});
	
	// Text elements
	var getRowTextTopOffset = function( data ) { 
		return ( this.__scales.ySpatial( data.rowPosition + 0.5 ) - this.CONST.SPACING_PX * 0.5 ) + "px";
	}.bind(this);
	var getColumnTextLeftOffset = function( data ) { 
		return ( this.__scales.xSpatial( data.columnPosition + 0.5 ) + this.__topLabelOffsetX ) + "px";
	}.bind(this);
	this.__elements.push({
		"identifier" : "div.rowTextsLeft",
		"layer" : this.__layers.leftPanel,
		"dataID" : "transitionRowElements",
		"renderers" : {
			"initRenderer" : function(e) {
				e.style( "left", "0px" )
				 .style( "width", this.CONST.LEFT_PANEL_WIDTH + "px" )
				 .style( "height", this.CONST.SPACING_PX + "px" )
				 .style( "font-size", this.CONST.FONT_SIZE_PT + "pt" )
				 .style( "text-align", "right" )
				 .style( "white-space", "nowrap" )
			},
			"updateAnimations" : function(e) {
				e.style( "top", getRowTextTopOffset )
				 .style( "color", this.__getForegroundColor.bind(this) )
				 .style( "font-weight", this.__getFontWeight.bind(this) )
				 .style( "text-decoration", this.__getTextDecoration.bind(this) )
				 .text( function(d) { return d.text } )
			},
			"mouse" : this.mouseListeners,
			"dragdrop" : this.dragdropListeners
		}
	});
	this.__elements.push({
		"identifier" : "div.columnTexts",
		"layer" : this.__layers.topPanel,
		"dataID" : "transitionColumnElements",
		"renderers" : {
			"initRenderer" : function(e) {
				e.style( "top", ( this.CONST.TOP_PANEL_HEIGHT + this.__topLabelOffsetY ) + "px" )
				 .style( "width", this.__topLabelWidth + "px" )
				 .style( "height", this.__topLabelHeight + "px" )
				 .style( "font-size", this.CONST.FONT_SIZE_PT + "pt" )
				 .style( "text-align", "left" )
				 .style( "white-space", "nowrap" )
				 .style( "-webkit-transform", "rotate(" +this.__topLabelAngle+ "deg)" )
				 .style( "-moz-transform", "rotate(" +this.__topLabelAngle+ "deg)" )
				 .style( "-o-transform", "rotate(" +this.__topLabelAngle+ "deg)" )
				 .style( "cursor", "pointer" )
				e.append( "span" ).attr( "class", "text" ).style( "position", "static" ).style( "pointer-events", "none" );
				e.append( "span" ).attr( "class", "icons" ).style( "position", "static" ).style( "pointer-events", "none" );
			},
			"updateRenderer" : function(e) {
				var iconsBox = e.select( "span.icons" ).selectAll( "i" ).data( function(d) { return d.icons.split(";") } );
				iconsBox.exit().remove();
				iconsBox.enter().append( "i" )
				 .style( "padding-left", "4px" )
				 .style( "position", "static" )
			},
			"updateAnimations" : function(e) {
				e.style( "left", getColumnTextLeftOffset )
				 .style( "color", this.__getForegroundColor.bind(this) )
				 .style( "font-weight", this.__getFontWeight.bind(this) )
				 .style( "text-decoration", this.__getTextDecoration.bind(this) )
				e.select( "span.text" )
				 .text( function(d) { return d.text } );
				e.select( "span.icons" ).selectAll( "i" )
				 .attr( "class", function(d) { return this.CONST.ICONS[ d.toUpperCase() ] }.bind(this) );
			},
			"mouse" : this.mouseListeners,
			"dragdrop" : this.dragdropListeners
		}
	});
	this.__elements.push({
		"identifier" : "div.rowTextsRight",
		"layer" : this.__layers.rightPanel,
		"dataID" : "transitionRowElements",
		"renderers" : {
			"initRenderer" : function(e) {
				e.style( "left", "0px" )
				 .style( "width", this.CONST.RIGHT_PANEL_WIDTH + "px" )
				 .style( "height", this.CONST.SPACING_PX + "px" )
				 .style( "font-size", this.CONST.FONT_SIZE_PT + "pt" )
				 .style( "text-align", "right" )
				 .style( "white-space", "nowrap" )
			},
			"updateAnimations" : function(e) {
				e.style( "top", getRowTextTopOffset )
				 .style( "color", this.__getForegroundColor.bind(this) )
				 .style( "font-weight", this.__getFontWeight.bind(this) )
				 .style( "text-decoration", this.__getTextDecoration.bind(this) )
				 .text( function(d) { return d.text } )
			},
			"mouse" : this.mouseListeners,
			"dragdrop" : this.dragdropListeners
		}
	});

	// Totals and subtotals
	var transformRowTotals = function( d ) { 
		return "translate(0," + this.__scales.ySpatial( d.rowPosition + 0.5 ) + ")";
	}.bind(this);
	var transformColumnTotals = function( d ) {
		return "translate(" + this.__scales.xSpatial( d.columnPosition + 0.5 ) + ",0)";
	}.bind(this);
	this.__elements.push({
		"identifier" : "line.rowTotals",
		"layer" : this.__layers.farPanel, 
		"dataID" : "transitionRowElements",
		"renderers" : {
			"initRenderer" : function(e) {
				e.attr( "y1", 0 )
				 .attr( "y2", 0 )
				 .style( "stroke-width", this.CONST.BAR_WIDTH_PX )
			},
			"updateAnimations" : function(e) {
				e.attr( "transform", transformRowTotals )
				 .attr( "x1", this.__scales.xLength(0) )
				 .attr( "x2", function(d) { return this.__scales.xLength(d.value) }.bind(this) )
				 .style( "stroke", this.__getBackgroundColor.bind(this) )
				 .style( "stroke-opacity", this.__getTotalStrokeOpacity.bind(this) )
			},
			"mouse" : this.mouseListeners
		}
	});
	this.__elements.push({
		"identifier" : "line.columnTotals",
		"layer" : this.__layers.bottomPanel, 
		"dataID" : "transitionColumnElements",
		"renderers" : {
			"initRenderer" : function(e) {
				e.attr( "x1", 0 )
				 .attr( "x2", 0 )
				 .style( "stroke-width", this.CONST.BAR_WIDTH_PX )
			},
			"updateAnimations" : function(e) {
				e.attr( "transform", transformColumnTotals )
				 .attr( "y1", this.__scales.yLength(0) )
				 .attr( "y2", function(d) { return this.__scales.yLength(d.value) }.bind(this) )
				 .style( "stroke", this.__getBackgroundColor.bind(this) )
				 .style( "stroke-opacity", this.__getTotalStrokeOpacity.bind(this) )
			},
			"mouse" : this.mouseListeners
		}
	});

	this.__elements.push({
		"identifier" : "line.rowSubtotals",
		"layer" : this.__layers.farPanel, 
		"dataID" : "transitionRowCrossRefs",
		"renderers" : {
			"initRenderer" : function(e) {
				e.attr( "y1", 0 )
				 .attr( "y2", 0 )
				 .style( "stroke-width", this.CONST.BAR_WIDTH_PX )
			},
			"updateAnimations" : function(e) {
				e.attr( "transform", transformRowTotals )
				e.attr( "x1", function(d) { return this.__scales.xLength(d.startValue) }.bind(this) )
				 .attr( "x2", function(d) { return this.__scales.xLength(d.endValue) }.bind(this) );
				e.style( "stroke", this.__getForegroundColor.bind(this) )
				 .style( "stroke-opacity", this.__getSubtotalStrokeOpacity.bind(this) )
			},
			"mouse" : this.mouseListeners
		}
	});
	this.__elements.push({
		"identifier" : "line.columnSubtotals",
		"layer" : this.__layers.bottomPanel, 
		"dataID" : "transitionColumnCrossRefs",
		"renderers" : {
			"initRenderer" : function(e) {
				e.attr( "x1", 0 )
				 .attr( "x2", 0 )
				 .style( "stroke-width", this.CONST.BAR_WIDTH_PX )
			},
			"updateAnimations" : function(e) {
				e.attr( "transform", transformColumnTotals )
				e.attr( "y1", function(d) { return this.__scales.yLength(d.startValue) }.bind(this) )
				 .attr( "y2", function(d) { return this.__scales.yLength(d.endValue) }.bind(this) );
				e.style( "stroke", this.__getForegroundColor.bind(this) )
				 .style( "stroke-opacity", this.__getSubtotalStrokeOpacity.bind(this) )
			},
			"mouse" : this.mouseListeners
		}
	});
	
	var getMinVisibleRowQuantile = function( data ) {
		return this.state.CONST.MIN_VISIBLE_ROW_QUANTILE;
	}.bind(this);
	var getMaxVisibleRowQuantile = function( data ) {
		return this.state.CONST.MAX_VISIBLE_ROW_QUANTILE;
	}.bind(this);
	var getVisibleRowQuantile = function( data ) {
		var columnVisibleRowQuantiles = this.state.get( "columnVisibleRowQuantiles" );
		var quantile = undefined;
		if ( columnVisibleRowQuantiles.hasOwnProperty( data.columnIndex ) )
			quantile = columnVisibleRowQuantiles[ data.columnIndex ];
		else
			quantile = this.state.get( "expansionVisibleRowQuantile" );
		return quantile;
	}.bind(this);
	var getMinOrderedRowQuantile = function( data ) {
		return this.state.CONST.MIN_ORDERED_ROW_QUANTILE;
	}.bind(this);
	var getMaxOrderedRowQuantile = function( data ) {
		return this.state.CONST.MAX_ORDERED_ROW_QUANTILE;
	}.bind(this);
	var getOrderedRowQuantile = function( data ) {
		var columnOrderedRowQuantiles = this.state.get( "columnOrderedRowQuantiles" );
		var quantile = undefined;
		if ( columnOrderedRowQuantiles.hasOwnProperty( data.columnIndex ) )
			quantile = columnOrderedRowQuantiles[ data.columnIndex ];
		else
			quantile = this.state.get( "expansionOrderedRowQuantile" );
		return quantile;
	}.bind(this);
	var onChangeColumnLabel = function( data ) {
		this.state.columnLabels( data.columnIndex, d3.event.srcElement.value );
		d3.event.srcElement.blur();
	}.bind(this);
	var onChangeVisibleRowQuantile = function( data ) {
		var quantile = parseInt(d3.event.srcElement.value);
		this.state.columnVisibleRowQuantiles( data.columnIndex, quantile );
	}.bind(this);
	var onChangeOrderedRowQuantile = function( data ) {
		var quantile = parseInt(d3.event.srcElement.value);
		this.state.columnOrderedRowQuantiles( data.columnIndex, quantile );
	}.bind(this);
	this.__elements.push({
		"identifier" : "div.columnMetas",
		"layer" : this.__layers.topCatcher,
		"dataID" : "transitionColumnMetas",
		"renderers" : {
			"initRenderer" : function(e) {
				e.style( "top", "0px" )
				 .style( "width", this.CONST.EXPANSION_SPACING + "px" )
				 .style( "height", this.CONST.TOP_PANEL_HEIGHT + "px" )
				var textBox = e.append( "div" )
					.attr( "class", "columnText" )
					.style( "left", this.CONST.EXPANSION_OFFSET + this.CONST.SPACING_PX * 2.5 + "px" )
					.style( "top", "0px" )
				textBox.append( "input" )
					.attr( "type", "text" )
					.style( "color", this.CONST.DEFAULT_COLOR )
					.style( "border", "2px dotted #fff" )
					.style( "padding", "2px" )
					.style( "font-size", this.CONST.FONT_SIZE_PT * 1.35 + "pt" )
					.style( "font-weight", "bold" )
					.style( "width", this.CONST.EXPANSION_WIDTH + "px" )
					.style( "cursor", "text" )
					.style( "pointer-events", "auto" )
					.on( "mouseover", function() { d3.select(d3.event.srcElement).style( "border-color", this.CONST.DEFAULT_COLOR ) }.bind(this) )
					.on( "mouseout", function() { d3.select(d3.event.srcElement).style( "border-color", "#fff" ) }.bind(this) )
					.on( "focus", function() { d3.select(d3.event.srcElement).style( "border-color", "#fff" ) }.bind(this) )
					.on( "keydown", function() { d3.event.cancelBubble = true } )
					.on( "change", onChangeColumnLabel )
				var visibilityBox = e.selectAll( "div.visibility" ).data( function(d) { return d.visibility } ).enter()
					.append( "div" )
					.attr( "class", "visibility" )
					.style( "left", this.CONST.EXPANSION_OFFSET + this.CONST.SPACING_PX * 2.5 + 10 + "px" )
					.style( "top", "30px" )
					.style( "width", "125px" )
					.style( "height", "16px" )
					.style( "pointer-events", "auto" )
				visibilityBox.append( "div" )
					.append( "i" )
					.attr( "class", this.CONST.ICONS.VISIBILITY )
					.style( "color", this.CONST.DEFAULT_COLOR )
					.style( "font-size", this.CONST.FONT_SIZE_PT+ "pt" )
					.style( "opacity", 0.75 )
				visibilityBox.append( "div" )
					.append( "input" )
					.attr( "type", "range" )
					.attr( "min", getMinVisibleRowQuantile )
					.attr( "max", getMaxVisibleRowQuantile )
					.attr( "value", getVisibleRowQuantile )
					.style( "left", "14px" )
					.style( "top", "-1px" )
					.style( "width", "90px" )
					.style( "opacity", 0.3 )
					.style( "cursor", "pointer" )
					.style( "pointer-events", "auto" )
					.on( "mouseover", function() { d3.select(d3.event.srcElement).transition().style( "opacity", 1 ) } )
					.on( "mouseout", function() { d3.select(d3.event.srcElement).transition().style( "opacity", 0.3 ) } )
					.on( "change", onChangeVisibleRowQuantile )
				var orderingBox = e.selectAll( "div.ordering" ).data( function(d) { return d.ordering } ).enter()
					.append( "div" )
					.attr( "class", "ordering" )
					.style( "left", this.CONST.EXPANSION_OFFSET + this.CONST.SPACING_PX * 2.5 + 10 + "px" )
					.style( "top", "45px" )
					.style( "width", "125px" )
					.style( "height", "16px" )
					.style( "pointer-events", "auto" )
				orderingBox.append( "div" )
					.append( "i" )
					.attr( "class", this.CONST.ICONS.ORDERING )
					.style( "color", this.CONST.DEFAULT_COLOR )
					.style( "font-size", this.CONST.FONT_SIZE_PT+ "pt" )
					.style( "opacity", 0.75 )
				orderingBox.append( "div" )
					.append( "input" )
					.attr( "type", "range" )
					.attr( "min", getMinOrderedRowQuantile )
					.attr( "max", getMaxOrderedRowQuantile )
					.attr( "value", getOrderedRowQuantile )
					.style( "left", "14px" )
					.style( "top", "-1px" )
					.style( "width", "90px" )
					.style( "opacity", 0.1 )
					.style( "cursor", "pointer" )
					.style( "pointer-events", "auto" )
					.on( "mouseover", function() { d3.select(d3.event.srcElement).transition().style( "opacity", 1 ) } )
					.on( "mouseout", function() { d3.select(d3.event.srcElement).transition().style( "opacity", 0.3 ) } )
					.on( "change", onChangeOrderedRowQuantile )
			},
			"updateAnimations" : function(e) {
				e.style( "left", ( this.__scales.xSpatial( this.model.get("expansionColumnPosition") ) + this.CONST.SPACING_PX ) + "px" )
				e.select( "div.columnText" ).select( "input" )
					.each( function(d) { d3.select(this)[0][0].value = d.element.text } )
			},
			"mouse" : this.mouseListeners
		}
	});
	
	var onClickPromotions = function( data ) {
		if ( data.isPromoted )
			this.state.entryPromotionsAndDemotions( data.rowIndex, data.columnIndex );
		else
			this.state.entryPromotionsAndDemotions( data.rowIndex, data.columnIndex, true );
		d3.event.cancelBubble = true;
	}.bind(this);
	var onClickDemotions = function( data ) {
		if ( data.isDemoted )
			this.state.entryPromotionsAndDemotions( data.rowIndex, data.columnIndex );
		else
			this.state.entryPromotionsAndDemotions( data.rowIndex, data.columnIndex, false );
		d3.event.cancelBubble = true;
	}.bind(this);
	var onMouseOverProDemotions = function() {
		d3.select( d3.event.srcElement ).transition().style( "color", this.CONST.DEFAULT_COLOR );
	}.bind(this);
	var onMouseOutProDemotions = function() {
		d3.select( d3.event.srcElement ).transition().style( "color", this.CONST.DEFAULT_BACKGROUND );
	}.bind(this);
	this.__elements.push({
		"identifier" : "div.annotationBorder",
		"layer" : this.__layers.centerControls,
		"dataID" : "transitionColumnMetas",
		"renderers" : {
			"initRenderer" : function(e) {
				e.style( "width", this.CONST.EXPANSION_WIDTH + this.CONST.SPACING_PX * 0.5 + "px" )
				 .style( "border", "1px solid #ccc" )
				 .style( "box-shadow", "0 0 10px #999" )
				 .style( "background", "#fff" );
			},
			"updateAnimations" : function(e) {
				e.style( "left", ( this.__scales.xSpatial( this.model.get("expansionColumnPosition") ) + this.CONST.EXPANSION_OFFSET + this.CONST.SPACING_PX * 2 ) + "px" )
				 .style( "top", ( this.__scales.ySpatial(0) - this.CONST.SPACING_PX * 0.5 - 2 ) + "px" )
				 .style( "height", function(d) { return ( this.model.get("visibleAnnotationDims") + 1.0 ) * this.CONST.SPACING_PX + "px" }.bind(this) )
			}
		}
	});
	this.__elements.push({
		"identifier" : "div.annotationItems",
		"layer" : this.__layers.centerControls,
		"dataID" : "transitionAnnotationControls",
		"renderers" : {
			"initRenderer" : function(e) {
				e.style( "height", this.CONST.SPACING_PX + "px" )
				 .style( "width", this.CONST.EXPANSION_WIDTH + "px" )
			 	 .style( "color", this.CONST.DEFAULT_COLOR )
				e.append( "div" )
					.attr( "class", "promoteButton" )
					.style( "left", function(d,i) { return this.CONST.SPACING_PX * 0.5 + "px" }.bind(this) )
					.style( "width", this.CONST.SPACING_PX * 1.25 + "px" )
					.style( "height", this.CONST.SPACING_PX + "px" )
			 	 	.style( "color", this.CONST.DEFAULT_BACKGROUND )
					.style( "cursor", "pointer" )
					.style( "pointer-events", "auto" )
					.on( "click", onClickPromotions )
					.on( "mouseover", onMouseOverProDemotions )
					.on( "mouseout", onMouseOutProDemotions )
					.append( "i" )
						.style( "pointer-events", "none" )
						.style( "left", this.CONST.SPACING_PX * 0.125 + "px" )
						.style( "font-size", this.CONST.SPACING_PX + "px" );
				e.append( "div" )
				 	.attr( "class", "demoteButton" )
					.style( "left", function(d,i) { return this.CONST.SPACING_PX * 1.75 + "px" }.bind(this) )
					.style( "width", this.CONST.SPACING_PX * 1.25 + "px" )
					.style( "height", this.CONST.SPACING_PX + "px" )
			 	 	.style( "color", this.CONST.DEFAULT_BACKGROUND )
					.style( "cursor", "pointer" )
					.style( "pointer-events", "auto" )
					.on( "click", onClickDemotions )
					.on( "mouseover", onMouseOverProDemotions )
					.on( "mouseout", onMouseOutProDemotions )
					.append( "i" )
						.style( "pointer-events", "none" )
						.style( "left", this.CONST.SPACING_PX * 0.125 + "px" )
						.style( "font-size", this.CONST.SPACING_PX + "px" )
				e.append( "div" )
					.attr( "class", "rowText" )
					.style( "left", this.CONST.SPACING_PX * 3.25 + "px" )
				 	.style( "font-size", this.CONST.FONT_SIZE_PT + "pt" )
					.text( function(d) { return d.text } );
			},
			"updateAnimations" : function(e) {
				e.style( "top", function(d) { return ( this.__scales.ySpatial(d.rowPosition) - 2 ) + "px" }.bind(this) )
				 .style( "left", function(d) { return ( this.__scales.xSpatial(d.columnPosition) + this.CONST.EXPANSION_OFFSET + this.CONST.SPACING_PX * 2.25 ) + "px" }.bind(this) );
				e.select( "div.promoteButton" )
					.select( "i" )
						.style( "color", function(d) { return d.isPromoted ? this.CONST.HIGHLIGHT_COLOR : ( d.isDemoted ? "#fff" : null ) }.bind(this) )
						.attr( "class", function(d) { return d.isPromoted ? this.CONST.ICONS.PROMOTIONS : this.CONST.ICONS.NO_PROMOTIONS }.bind(this) )
				e.select( "div.demoteButton" )
					.select( "i" )
						.style( "color", function(d) { return d.isPromoted ? "#fff" : ( d.isDemoted ? "#e7e7e7" : null ) }.bind(this) )
						.attr( "class", function(d) { return d.isDemoted ? this.CONST.ICONS.DEMOTIONS : this.CONST.ICONS.NO_DEMOTIONS }.bind(this) )
				e.select( "div.rowText" )
					.style( "color", function(d) { return d.isPromoted ? this.CONST.HIGHLIGHT_COLOR : ( d.isDemoted ? "#dfdfdf" : null ) }.bind(this) )
					.style( "font-weight", function(d) { return d.isPromoted ? "bold" : null }.bind(this) )
					.style( "text-decoration", function(d) { return d.isDemoted ? "line-through" : null }.bind(this) )
			},
			"mouse" : this.mouseListeners
		}
	});

};

//--------------------------------------------------------------------------------------------------

MatrixView.prototype.__resetElements = function() {
	if ( this.__getDirtyModel() === true ) {
		for ( var i = 0; i < this.__elements.length; i++ ) {
			var element = this.__elements[i];
			var identifier = element.identifier;
			var layer = element.layer.content;
			layer.selectAll( identifier ).remove();
			this.setDirty( "elements", identifier );
		}
	}
};

MatrixView.prototype.__renderElements = function() {
	var visSchedules = this.model.get( "vis:schedules" );
	
	for ( var i = 0; i < this.__elements.length; i++ ) {
		var element = this.__elements[i];
		var identifier = element.identifier;
		var layer = element.layer.content;
		var renderers = element.renderers;
		var visSchedule = visSchedules[ element.dataID ];
		
		// Bind data and create new HTML elements
		if ( visSchedule.isEnter ) {
			var tagName = identifier.substr( 0, identifier.indexOf( "." ) );
			var className = identifier.substr( identifier.indexOf( "." ) + 1 );
			var data = this.model.get( element.dataID );
			layer.selectAll( identifier ).data( data ).enter().append( tagName )
				.call( enterRenderer, className );
		}
		
		// Create { enter, stay, exit } transitions
		var allContent = layer.selectAll( identifier );
		
		// Enter transitions
		if ( visSchedule.isEnter ) {
			var enterContent = allContent.filter( function(d) { return d.isEnter } );
			var enterSchedule = visSchedule[ "enter" ];
			for ( var r in renderers )
				enterContent.call( renderers[r].bind(this) );
			var enterTransition = enterContent.transition().duration( enterSchedule.duration ).delay( enterSchedule.delay ).ease( enterSchedule.ease );
			enterTransition.call( enterAnimations.bind(this) );
			this.setDirty( "elements", identifier, "enter", enterTransition.size() );
		}
		
		// Exit transitions
		if ( visSchedule.isExit ) {
			var exitContent = allContent.filter( function(d) { return d.isExit } );
			var exitSchedule = visSchedule[ "exit" ];
			var exitTransition = exitContent.transition().duration( exitSchedule.duration ).delay( exitSchedule.delay ).ease( exitSchedule.ease );
			exitTransition.call( exitAnimations.bind(this) );
			this.setDirty( "elements", identifier, "exit", exitTransition.size() );
		}
		
		// Stay transitions
		if ( visSchedule.isStay ) {
			var stayContent = allContent.filter( function(d) { return d.isStay } );
			var staySchedule = visSchedule[ "stay" ];
			
			var renderAll = false;
			var renderStay = false;
			var dirty;

			// If scales changed, force all to be refreshed
			if ( this.isDirty( "scales" ) ) {
				renderAll = true;
			}
			// Check whether underlying data changed
			if ( ! renderAll ) {
				var dirtyID = element.dataID.replace( /^transition/, "all" );
				if ( this.__isDirtyModel( dirtyID ) )
					var dirty = this.__getDirtyModel( dirtyID );
				if ( dirty === true )
					renderAll = true;
				else if ( dirty !== undefined )
					renderStay = true;
			}

			// Render
			if ( renderAll ) {
				if ( renderers.hasOwnProperty( "updateRenderer" ) )
					stayContent.call( renderers.updateRenderer.bind(this) );
				var stayTransition = stayContent.transition().duration( staySchedule.duration ).delay( staySchedule.delay ).ease( staySchedule.ease );
				stayTransition.call( enterAnimations.bind(this) );
				if ( renderers.hasOwnProperty( "updateAnimations" ) )
					stayTransition.call( renderers.updateAnimations.bind(this) );
				if ( stayTransition.size() > 0 )
					this.setDirty( "elements", identifier, "stay", stayTransition.size() );
			}
			else if ( renderStay ) {
				if ( renderers.hasOwnProperty( "updateRenderer" ) )
					stayContent.call( renderers.updateRenderer.bind(this) );
				var dirtyContent = stayContent.filter( function(d) { return dirty.hasOwnProperty( d.key ) } );
				var dirtyTransition = dirtyContent.transition().duration( staySchedule.duration ).delay( staySchedule.delay ).ease( staySchedule.ease );
				dirtyTransition.call( enterAnimations.bind(this) );
				if ( renderers.hasOwnProperty( "updateAnimations" ) )
					dirtyTransition.call( renderers.updateAnimations.bind(this) );
				if ( dirtyTransition.size() > 0 )
					this.setDirty( "elements", identifier, "dirty", dirtyTransition.size() );
			}
		}
	}
	function enterRenderer( e, className ) {
		e.attr( "class", className )
		 .style( "opacity", 0 )
	}
	function enterAnimations( e ) { 
		e.style( "opacity", 1 ) 
	}
	function exitAnimations( e ) {
		e.attr( "class", null )
		 .style( "opacity", 0 )
		 .remove()
	}
};

MatrixView.prototype.__resizeLayers = function() {
	if ( this.isDirty( "scales", [ "chartWidth", "chartHeight" ] ) ) {
		var schedule = this.model.get( "vis:schedules" )[ "vis" ]
		var preSchedule = schedule[ "pre" ];
		var postSchedule = schedule[ "post" ];

		var currentChartWidth = this.__scales.chartWidth;
		var currentChartHeight = this.__scales.chartHeight;
		var previousChartWidth = this.__scales.previousChartWidth;
		var previousChartHeight = this.__scales.previousChartHeight;
		var leadingAnimation = ( currentChartWidth > previousChartWidth || currentChartHeight > previousChartHeight );

		for ( var layerID in this.__layers ) {
			var layer = this.__layers[ layerID ];
			var dims = layer.dims.bind(this);
			var currentDims = dims( currentChartWidth, currentChartHeight );
			var previousDims = dims( previousChartWidth, previousChartHeight );
			
			var renderer = layer.renderer.bind(this);
			layer.content.transition().duration( preSchedule.duration ).delay( preSchedule.delay ).ease( preSchedule.ease )
				.call( renderer, ( leadingAnimation ) ? currentDims : previousDims );
			layer.content.transition().duration( postSchedule.duration ).delay( postSchedule.delay ).ease( postSchedule.ease )
				.call( renderer, currentDims );
		}
	}
};

MatrixView.prototype.__resizeContainerAndDepths = function() {
	if ( this.isDirty( "scales", [ "visWidth", "visHeight" ] ) ) {
		var schedule = this.model.get( "vis:schedules" )[ "vis" ]
		var preSchedule = schedule[ "pre" ];
		var postSchedule = schedule[ "post" ];

		var container = this.__container;
		var currentWidth = this.__scales.visWidth;
		var currentHeight = this.__scales.visHeight;
		var previousWidth = container[0][0].offsetWidth - 2;   // Account for 1px border on both sides
		var previousHeight = container[0][0].offsetHeight - 2; // Account for 1px border on both sides
		
		container.transition().duration( preSchedule.duration ).delay( preSchedule.delay ).ease( preSchedule.ease )
			.style( "width", ( currentWidth > previousWidth ) ? currentWidth + "px" : previousWidth + "px" )
			.style( "height", ( currentHeight > previousHeight ) ? currentHeight + "px" : previousHeight + "px" )
		container.transition().duration( postSchedule.duration ).delay( postSchedule.delay ).ease( postSchedule.ease )
			.style( "width", currentWidth + "px" )
			.style( "height", currentHeight + "px" );
		for ( var id in this.__depths ) {
			var depth = this.__depths[id];
			depth.transition().duration( preSchedule.duration ).delay( preSchedule.delay ).ease( preSchedule.ease )
				.style( "width", ( currentWidth > previousWidth ) ? currentWidth + "px" : previousWidth + "px" )
				.style( "height", ( currentHeight > previousHeight ) ? currentHeight + "px" : previousHeight + "px" )
			depth.transition().duration( postSchedule.duration ).delay( postSchedule.delay ).ease( postSchedule.ease )
				.style( "width", currentWidth + "px" )
				.style( "height", currentHeight + "px" );
		}
	}
};

//------------------------------------------------------------------------------

MatrixView.prototype.__calculateChartWidthAndColumnLayouts = function() {
	this.__scales.previousChartWidth = this.__scales.chartWidth || 0;
	if ( this.__isDirtyModel( "visibleColumnDims" ) || this.__isDirtyModel( "expansionColumnPosition" ) ) {
		var columnDims = this.model.get( "visibleColumnDims" );
		var chartWidth = this.CONST.SPACING_PX * columnDims;
		var xSpatial = d3.scale.linear().domain( [ 0, columnDims ] ).range( [ 0, chartWidth ] );

		var expansionColumnPosition = this.model.get( "expansionColumnPosition" );
		if ( expansionColumnPosition !== undefined ) {
			chartWidth += this.CONST.EXPANSION_SPACING;
			var xLeftSpatial = xSpatial;
			var xRightSpatial = d3.scale.linear().domain( [ 0, columnDims ] ).range( [ this.CONST.EXPANSION_SPACING, chartWidth ] );
			xSpatial = function( d ) {
				if ( d < expansionColumnPosition + 0.5 )
					return xLeftSpatial( d );
				else if ( d > expansionColumnPosition + 0.5 )
					return xRightSpatial( d );
				else
					return xLeftSpatial( expansionColumnPosition ) + this.CONST.EXPANSION_OFFSET + this.CONST.SPACING_PX / 2;
			}.bind(this);
		}

		this.__scales.columnDims = columnDims;
		this.__scales.chartWidth = chartWidth;
		this.__scales.xSpatial = xSpatial;
		this.setDirty( "scales", [ "columnDims", "chartWidth", "xSpatial" ] );
	}
};

MatrixView.prototype.__calculateChartHeightAndRowLayouts = function() {
	this.__scales.previousChartHeight = this.__scales.chartHeight || 0;
	if ( this.__isDirtyModel( "visibleRowDims" ) ) {
		var rowDims = this.model.get( "visibleRowDims" );
		var chartHeight = this.CONST.SPACING_PX * rowDims;
		var ySpatial = d3.scale.linear().domain( [ 0, rowDims ] ).range( [ 0, chartHeight ] );

		this.__scales.rowDims = rowDims;
		this.__scales.chartHeight = chartHeight;
		this.__scales.ySpatial = ySpatial;
		this.setDirty( "scales", [ "rowDims", "chartHeight", "ySpatial" ] );
	}
};

MatrixView.prototype.__calculateSizes = function() {
	if ( this.__isDirtyModel( "maxValue" ) ) {
		var maxValue = this.model.get( "maxValue" );
		var rSize = d3.scale.sqrt().domain( [ 0, maxValue ] ).range( [ 0, this.CONST.MAX_RADIUS_PX ] );
		this.__scales.rSize = rSize;
		this.setDirty( "scales", "rSize" );
	}
	if ( this.__isDirtyModel( "maxRowValue" ) ) {
		var maxRowValue = this.model.get( "maxRowValue" );
		var xLength = d3.scale.linear().domain( [ 0, maxRowValue ] ).range( [ 0, this.CONST.FAR_BAR_MAX_LENGTH ] );
		this.__scales.xLength = xLength;
		this.setDirty( "scales", "xLength" );
	}
	if ( this.__isDirtyModel( "maxColumnValue" ) ) {
		var maxColumnValue = this.model.get( "maxColumnValue" );
		var yLength = d3.scale.linear().domain( [ 0, maxColumnValue ] ).range( [ 0, this.CONST.BOTTOM_BAR_MAX_LENGTH ] );
		this.__scales.yLength = yLength;
		this.setDirty( "scales", "yLength" );
	}
};

MatrixView.prototype.__calculateDimensions = function() {
	if ( this.isDirty( "scales", [ "chartWidth", "chartHeight" ] ) )
	{
		var chartWidth = this.__scales.chartWidth;
		var chartHeight = this.__scales.chartHeight;
		var visWidth = 
			this.CONST.OUTER_PADDING + 
			this.CONST.LEFT_PANEL_WIDTH + this.CONST.LEFT_PADDING + 
			chartWidth + this.CONST.RIGHT_PADDING + 
			this.CONST.RIGHT_PANEL_WIDTH + this.CONST.FAR_PADDING + 
			this.CONST.FAR_PANEL_WIDTH + this.CONST.OUTER_PADDING;
		var visHeight = 
			this.CONST.OUTER_PADDING + 
			this.CONST.TOP_PANEL_HEIGHT + this.CONST.TOP_PADDING + 
			chartHeight + this.CONST.BOTTOM_PADDING + 
			this.CONST.BOTTOM_PANEL_HEIGHT + this.CONST.OUTER_PADDING;
		this.__scales.visWidth = visWidth;
		this.__scales.visHeight = visHeight;
		this.setDirty( "scales", [ "visWidth", "visHeight" ] );
	}
};

//==================================================================================================

MatrixView.prototype.__getForegroundColor = function( d ) {
	var selectionGroups = this.model.get( "allSelectionGroups" );
	if ( d.isSelected )
		return selectionGroups[ d.selectionIndex ].color;
	if ( d.isHighlighted )
		if ( this.model.get( "highlightSelectionIndex" ) !== undefined )
			return selectionGroups[ this.model.get( "highlightSelectionIndex" ) ].color;
		else
			return this.CONST.HIGHLIGHT_COLOR;
	return this.CONST.DEFAULT_COLOR;
};
MatrixView.prototype.__getBackgroundColor = function( d ) {
	var selectionGroups = this.model.get( "allSelectionGroups" );
	if ( d.isSelected )
		return selectionGroups[ d.selectionIndex ].background;
	if ( d.isHighlighted )
		if ( this.model.get( "highlightSelectionIndex" ) !== undefined )
			return selectionGroups[ this.model.get( "highlightSelectionIndex" ) ].background;
		else
			return this.CONST.HIGHLIGHT_BACKGROUND;
	return this.CONST.DEFAULT_BACKGROUND;
};

MatrixView.prototype.__getFontWeight = function( d ) {
	if ( d.isHighlighted )
		return "bold";
	else
		return null;
};
MatrixView.prototype.__getTextDecoration = function( d ) {
	return null;
};

MatrixView.prototype.__getCircleStrokeWidth = function( d ) {
	if ( d.isDemoted )
		return 0;
	if ( d.isHighlighted )
		return 2.4;
	else
		return 0.8;
};
MatrixView.prototype.__getCircleStrokeOpacity = function( d ) {
	if ( d.isPromoted )
		return 1.0;
	if ( d.isDemoted )
		return 0.3;
	return 1.0;
};
MatrixView.prototype.__getCircleFillOpacity = function( d ) {
	if ( d.isPromoted )
		return 0.85;
	if ( d.isDemoted )
		return 0.1;
	return 0.3;
};
MatrixView.prototype.__getGridlineStrokeWidth = function( d ) {
	if ( d.isHighlighted )
		return 1.2;
	else
		return 0.6;
};
MatrixView.prototype.__getGridlineStrokeOpacity = function( d ) {
	return 1.0;
};
MatrixView.prototype.__getTotalStrokeOpacity = function( d ) {
	return 1.0;
};
MatrixView.prototype.__getSubtotalStrokeOpacity = function( d ) {
	if ( d.isHighlighted )
		return 1.0;
	else
		return 0.8;
};

//------------------------------------------------------------------------------

MatrixView.prototype.__topLabelAngle = MatrixView.prototype.CONST.TOP_LABEL_ANGLE_DEG;
MatrixView.prototype.__topLabelWidth = MatrixView.prototype.CONST.TOP_PANEL_HEIGHT;
MatrixView.prototype.__topLabelHeight = MatrixView.prototype.SPACING_PX;
MatrixView.prototype.__topLabelOffsetX = ( function() {
	var theta = MatrixView.prototype.CONST.TOP_LABEL_ANGLE_DEG;
	var cos = Math.cos( theta * Math.PI / 180 );
	var sin = Math.sin( theta * Math.PI / 180 );
	var halfWidth = MatrixView.prototype.CONST.TOP_PANEL_HEIGHT * 0.5;
	var halfHeight = MatrixView.prototype.CONST.SPACING_PX * 0.5;
	var xOffset = 0;                                               // Offset along the rotated x-axis
	var yOffset = -MatrixView.prototype.CONST.SPACING_PX * 0.5;    // Offset along the rotated y-axis
	var xCorrection = cos * halfWidth - sin * halfHeight + cos * xOffset - sin * yOffset;
	return -halfWidth + xCorrection;
} )();
MatrixView.prototype.__topLabelOffsetY = ( function() {
	var theta = MatrixView.prototype.CONST.TOP_LABEL_ANGLE_DEG;
	var cos = Math.cos( theta * Math.PI / 180 );
	var sin = Math.sin( theta * Math.PI / 180 );
	var halfWidth = MatrixView.prototype.CONST.TOP_PANEL_HEIGHT * 0.5;
	var halfHeight = MatrixView.prototype.CONST.SPACING_PX * 0.5;
	var xOffset = 0;                                               // Offset along the rotated x-axis
	var yOffset = -MatrixView.prototype.CONST.SPACING_PX * 0.5;    // Offset along the rotated y-axis
	var yCorrection = sin * halfWidth + cos * halfHeight + sin * xOffset + cos * yOffset;
	return -halfHeight + yCorrection;
} )();

//--------------------------------------------------------------------------------------------------
// Compatibility with Node.js

if ( typeof module !== "undefined" ) {
	module.exports = MatrixView;
}
