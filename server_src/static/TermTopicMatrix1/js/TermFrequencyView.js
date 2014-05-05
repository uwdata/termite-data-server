/*
	TermFrequencyView.js
	
	This view is responsible for generating the term frequency view.
	
	Details:
	--------
	Receives list of terms and associated frequencies from TermFrequencyModel. 
	
	Additionally, uses parameters defined in ViewParameters.js.
*/
var TERMFREQ_TEXT_DEFAULT = {
	FILL_COLOR: "#808080",
	STROKE_OPACITY: 0,
	FILL_OPACITY: 1
};
var TERMFREQ_BAR_DEFAULT = {
	STROKE_COLOR: "#808080",
	STROKE_WIDTH: 5,
	STROKE_OPACITY: 0.4
};
var HISTOGRAM_ENCODING_PARAMETERS = {
	NUM_TOPICS : 0,
	setNumTopics : function(numTopics) { this.NUM_TOPICS = numTopics; },
	DENSE_NUM_TOPICS: 50,
	LOOSE_NUM_TOPICS: 20,
	DENSE_PACKING: 12,
	LOOSE_PACKING: 18,
	packing : function()
	{
		return 12;
	}
};
var HISTORGRAM_CONTAINER_PADDING = {
	left_separation: 10,
	top: 60,
	left: 130, 
	right: 20,
	bottom: 60,
	width: 150,
	fullWidth : function() { return this.left + this.right + this.width },
	fullHeight : function( numTopics, numTerms ) { return this.top + this.bottom + HISTOGRAM_ENCODING_PARAMETERS.packing() * numTerms }
};
	
var TermFrequencyView = Backbone.View.extend({
	initialize : function() {
		this.parentModel = null;
		this.stateModel = null;
		
		// encoders
		this.ys = null;
		this.line_length = null;
		
		// svg layers
		this.svg = null;
		this.svgTermLabelLayer = null;
		this.svgTermBarLayer = null;
		this.overlayLayer = null;
		this.overlayLineLayer = null;
		this.svgTopicalBarLayer = null;
		this.svgTermHighlightLayer = null;
		
		// interaction variables
		this.highlightedTerm = null;
		this.highlightedTopic = null;
		
		this.colorClassPrefix = "HIST";
		this.normalColor = "normal";
		
		// bar highlighting
		this.totalOffsets = [];
		this.prevHighlightColor = this.normalColor;
		this.useOffset = false;
	}
});

/**
 * Initialize Term Frequency View's parent model
 *
 * @private
 */
TermFrequencyView.prototype.initModel = function( model, state ){
	this.parentModel = model;
	this.stateModel = state;
};

/**
 * Returns a list of "selected" topic objects or empty list
 *
 * @private
 */
TermFrequencyView.prototype.getSelectedTopics = function() {
	var selected = _.groupBy(this.stateModel.get("topicIndex"), "selected")['true'];
	if(selected !== undefined){
		return selected; 
	} else { return []; }
};

/** 
 * Initialize/render histogram view's elements for the first time
 *
 * @private
 */
TermFrequencyView.prototype.load = function(){
	this.renderInit();
	this.renderUpdate();
};

/** 
 * Updates the view (public encapsulation used in index.html)
 */
TermFrequencyView.prototype.update = function() {
	this.renderUpdate();
};

/**
 * Transforms the topical frequency matrix into a form appropriate for d3 stacked bars
 *
 * @private
 */
TermFrequencyView.prototype.prepareStackedBars = function() {
	var matrix = this.parentModel.get("topicalFreqMatrix");
	var stackedData = [];
	if( matrix.length > 0) {
		var remapped = matrix.map( function(layer){
			return layer.map( function(d, j) { return { x : j, y : d }; } );
		});
	
		var stackedTransformer = d3.layout.stack();
		stackedData = stackedTransformer(remapped);
	}
	
	// TODO: pull out as it own function?
	// update totalOffsets (for highlighting use)
    var topicMapping = _.object(_.map(this.stateModel.get("topicIndex"), 
    	function(t){return [t.id, t.selected]}));
    
    this.totalOffsets = [];
    if( stackedData.length > 1 || ((topicMapping[this.highlightedTopic] === false) && stackedData.length == 1)){
		for( var j = 0; j < stackedData[0].length; j++){
			var sum = 0.0;
			for( var i = 0; i < stackedData.length; i++){
				sum += stackedData[i][j].y;
			}
			this.totalOffsets[j] = sum;
		}
    }
    else { // fixes offset problem when removing last selected topic (highlight messing with it)
    	for( var j = 0; j < this.parentModel.get("termIndex").length; j++){
    		this.totalOffsets[j] = 0.0;
    	}
    }
    return stackedData;
};

/** 
 * Initialize histogram view's elements
 *	-svg layers
 *	-encoders
 *  -etc.
 *
 * @private
 */
TermFrequencyView.prototype.renderInit = function() {
	var termIndex = this.parentModel.get("termIndex");
	var termFreq = this.parentModel.get("totalTermFreqs");
		
	// Compute encoders
	this.ys = d3.scale.linear();
	
	var maxFreq = 0.0;
	for( var i = 0; i < termIndex.length; i++ ) {
		if(termFreq[termIndex[i]] > maxFreq)
			maxFreq = termFreq[termIndex[i]];
	}
	this.line_length = d3.scale.linear().domain([0, maxFreq]).range( [ 0, HISTORGRAM_CONTAINER_PADDING.width ] );

	// init svg layers
	var container =	d3.select(this.el);
	this.svg = container.append( "svg:svg" )
		.style( "cursor", "default" )
		.style( "width", HISTORGRAM_CONTAINER_PADDING.fullWidth() + "px" )
	this.svgTermLabelLayer = this.svg.append( "svg:g" )
		.attr( "class", "termLabelLayer" )
		.attr( "transform", "translate(" + HISTORGRAM_CONTAINER_PADDING.left + "," + HISTORGRAM_CONTAINER_PADDING.top + ")" );
	this.svgTermBarLayer = this.svg.append( "svg:g" )
		.attr( "class", "termBarLayer" )
		.attr( "transform", "translate(" + HISTORGRAM_CONTAINER_PADDING.left + "," + HISTORGRAM_CONTAINER_PADDING.top + ")" );
	this.overlayLayer = this.svg.append( "svg:g" )
		.attr( "class", "overlayLayer")
		.attr( "transform", "translate(" + HISTORGRAM_CONTAINER_PADDING.left + "," + HISTORGRAM_CONTAINER_PADDING.top + ")" );
	this.svgTopicalBarLayer = this.svg.append( "svg:g" )
		.attr( "class", "topicalBarLayer" )
		.attr( "transform", "translate(" + HISTORGRAM_CONTAINER_PADDING.left + "," + HISTORGRAM_CONTAINER_PADDING.top + ")" );
	this.svgTermHighlightLayer = this.svg.append( "svg:g" )
		.attr( "class", "termHighlightLayer" )
		.attr( "transform", "translate(" + HISTORGRAM_CONTAINER_PADDING.left + "," + HISTORGRAM_CONTAINER_PADDING.top + ")" );
};

/** 
 * Update histogram view's elements based on parent model's termIndex and term frequencies
 *
 * @private
 */
TermFrequencyView.prototype.renderUpdate = function() {
	var termIndex = this.parentModel.get("termIndex");
	var termFreq = this.parentModel.get("totalTermFreqs");

	this.svg
		.style( "height", HISTORGRAM_CONTAINER_PADDING.fullHeight( HISTOGRAM_ENCODING_PARAMETERS.NUM_TOPICS, termIndex.length ) + "px" )
	
	this.ys.domain( [ 0, termIndex.length ] )
		.range( [ 0, termIndex.length * HISTOGRAM_ENCODING_PARAMETERS.packing()] );

	this.svgTermLabelLayer.selectAll( "text" ).data( termIndex ).exit().remove();
	this.svgTermLabelLayer.selectAll( "text" ).data( termIndex ).enter().append( "svg:text" )
		.on( "mouseout", function() { this.trigger( "mouseout:term", "" ) }.bind(this))
		.attr( "x", -HISTORGRAM_CONTAINER_PADDING.left_separation )
		.attr( "y", 3 )
	this.svgTermLabelLayer.selectAll( "text" ).data( termIndex )	
		.attr( "class", function(d) { return ["termLabel", "HISTnormal", getTermClassTag(d)].join(" ") })
		.attr( "transform", function(d,i) { return "translate(0," + this.ys(i+0.5) + ")" }.bind(this) )
		.on( "mouseover", function(d) { this.trigger( "mouseover:term", d ) }.bind(this))
		.text( function(d) { return d } );

	this.svgTermBarLayer.selectAll("line").data(termIndex).exit().remove();
	this.svgTermBarLayer.selectAll("line").data(termIndex).enter().append("svg:line")
		.on( "mouseout", function() { this.trigger( "mouseout:term", "" ) }.bind(this) )
		.attr( "y1", 0 )
		.attr( "y2", 0 )
		.attr( "x1", this.line_length(0) )
	this.svgTermBarLayer.selectAll("line").data(termIndex)
		.attr( "transform", function(d,i) { return "translate(0," + this.ys(i+0.5) + ")" }.bind(this) )
		.attr( "class", function(d,i) { return ["termFreqBar", getTermClassTag(d)].join(" ") })
		.on( "mouseover", function(d) { this.trigger( "mouseover:term", d ) }.bind(this) )
		.attr( "x2", function(d) { return this.line_length(termFreq[d]) }.bind(this) )
	
	var stackedData = this.prepareStackedBars();
	var selectedTopics = this.getSelectedTopics();
	
	this.overlayLayer.selectAll( "g" ).data(stackedData).exit().remove();
	this.overlayLayer.selectAll( "g" ).data(stackedData).enter().append("svg:g")
	this.gLayer = this.overlayLayer.selectAll( "g" ).data(stackedData)
		.attr("class", function(d,i) { return ["overlayGroup", this.colorClassPrefix + selectedTopics[i].color].join(" ") }.bind(this) )
	
	this.gLayer.selectAll("line").data(function(d) {return d;}).exit().remove();
	this.gLayer.selectAll("line").data(function(d, i) { return d;}).enter().append("svg:line")
		.on( "mouseout", function() { this.trigger( "mouseout:term", "" ) }.bind(this) )
		.attr("y1", 0)
		.attr("y2", 0)
	this.gLayer.selectAll("line").data(function(d, i) { return d;})
		.attr("class", function(d,i){return ["line", getTermClassTag(termIndex[i])].join(" ") })
		.on( "mouseover", function(d, i) { this.trigger( "mouseover:term", termIndex[i]); }.bind(this) )
		.attr( "transform", function(d,i) { return "translate(0," + this.ys(i+0.5) + ")" }.bind(this) )
		.attr("x1", function(d){ return this.line_length(d.y0)}.bind(this) )
		.attr("x2", function(d){return this.line_length(d.y0) + this.line_length(d.y)}.bind(this) )
		
	this.svgTopicalBarLayer.selectAll("line").data( termIndex ).exit().remove();
	this.svgTopicalBarLayer.selectAll("line").data( termIndex ).enter().append("svg:line")
		.on( "mouseout", function() { this.trigger( "mouseout:term", "" ) }.bind(this) )
		.attr( "y1", 0 )
		.attr( "y2", 0 )
		.attr( "x1", this.line_length(0) )
		.attr( "x2", this.line_length(0) )
	this.svgTopicalBarLayer.selectAll("line").data(termIndex)
		.attr( "transform", function(d,i) { return "translate(0," + this.ys(i+0.5) + ")" }.bind(this) )
		.attr( "class", function(d,i) { return ["topicalFreqBar", getTermClassTag(d)].join(" ") })
		.on( "mouseover", function(d) { this.trigger( "mouseover:term", d ) }.bind(this) )
			
	this.svgTermHighlightLayer.selectAll("line").data(termIndex).exit().remove();
	this.svgTermHighlightLayer.selectAll("line").data(termIndex).enter().append("svg:line")
		.on( "mouseout", function() { this.trigger( "mouseout:term", "" ) }.bind(this) )
		.attr( "y1", 0 )
		.attr( "y2", 0 )
		.attr( "x1", this.line_length(0) )
		.style( "fill" , "none")
	this.svgTermHighlightLayer.selectAll("line").data( termIndex )
		.attr( "transform", function(d,i) { return "translate(0," + this.ys(i+0.5) + ")" }.bind(this) )
		.attr( "class", function(d,i) { return ["termHighlightBar", getTermClassTag(d)].join(" ") })
		.on( "mouseover", function(d) { this.trigger( "mouseover:term", d ) }.bind(this) )
		.attr( "x2", function(d) { return this.line_length(termFreq[d]) }.bind(this) )
};

// interactions
/** 
 * Calls appropriate functions to deal with topic highlight event elements
 *
 * @param { model } model is passed but unused
 * @param { int } value is the target topic
 * @return { void }
 */
TermFrequencyView.prototype.onHighlightTopicChanged = function( model, value ) {
	var topic = value;
	if(topic === null)
		this.unhighlight( false, true );
	else
		this.highlight( null, topic );
};
/** 
 * Calls appropriate functions to deal with term highlight event elements
 *
 * @param { model } model is passed but unused
 * @param { string } value is the target term
 * @return { void }
 */
TermFrequencyView.prototype.onHighlightTermChanged = function( model, value ) {
	var term = value;
	if(term === "")
		this.unhighlight( true, false );
	else
		this.highlight( term, null );
};
/** 
 * Unhighlights elements based on term and/or topic
 *
 * @private
 */
TermFrequencyView.prototype.unhighlight = function( term, topic ) {
	// unhighlight term
	if( term ){
		term = this.highlightedTerm;
		this.highlightedTerm = null;
		this.svgTermLabelLayer.selectAll("." + getTermClassTag(term))
			.classed(this.colorClassPrefix + HIGHLIGHT, false)
			
		this.svgTermHighlightLayer.selectAll("." + getTermClassTag(term))
			.classed(this.colorClassPrefix + HIGHLIGHT, false)
	} 
	
	// unhighlight topic
	if( topic ){
		topic = this.highlightedTopic;
		var termIndex = this.parentModel.get("termIndex");
		var topicals = this.parentModel.getTopicalsForTopic(topic);
		this.highlightedTopic = null;
		
		// highlight labels
		for( var i = 0; i < termIndex.length; i++){
			var term = termIndex[i];
			if( topicals[i]> THRESHHOLD ){
				this.svgTermLabelLayer.selectAll("." + getTermClassTag(term))	
					.classed(this.colorClassPrefix + HIGHLIGHT, false)
			
				if( this.useOffset ){
					// make highlight bars invis 
					this.svgTopicalBarLayer.selectAll("." + getTermClassTag(term))
						.classed(this.colorClassPrefix + HIGHLIGHT, false)
						.attr( "x2", this.line_length(0))
						.attr( "x1", this.line_length(0));
				}
			}
		}
		
		// UDPATE: ordered by appearance in matrix rather than order of selectoin
		// reset layers
		var selectedTopics = this.getSelectedTopics();
		if( selectedTopics.length > 0 ){
			this.gLayer = this.overlayLayer.selectAll( "g" )
				.attr("class", function(d,i) { return ["overlayGroup", this.colorClassPrefix + selectedTopics[i].color].join(" ") }.bind(this) );
		} else {
			this.gLayer = this.overlayLayer.selectAll( "g" )
				.attr("class", function(d,i) { return ["overlayGroup", this.colorClassPrefix + this.normalColor].join(" ") }.bind(this) );
		}

		
		// reset variables
		this.prevHighlightColor = this.normalColor;
		this.useOffset = false;
	}
};
/** 
 * Highlights elements based on term and/or topic
 *
 * @private
 */
TermFrequencyView.prototype.highlight = function( term, topic ) {
	// highlight term
	if( term !== null ){
		this.highlightedTerm = term;
		this.svgTermLabelLayer.selectAll("." + getTermClassTag(term))
			.classed(this.colorClassPrefix + HIGHLIGHT, true)
			
		this.svgTermHighlightLayer.selectAll("." + getTermClassTag(term))
			.classed(this.colorClassPrefix + HIGHLIGHT, true)
	} 
	// highlight topic
	else if( topic !== null ){
		var termIndex = this.parentModel.get("termIndex");
		var topicals = this.parentModel.getTopicalsForTopic(topic);
		this.highlightedTopic = topic;
		
		// highlight labels
		var stackedData = this.prepareStackedBars();
		var colors = [];
		var selectedTopics = this.getSelectedTopics();
		for( var i = 0; i < selectedTopics.length; i++ ){
			colors.push(selectedTopics[i].color);
		}

		var topicMapping = _.object(_.map(this.stateModel.get("topicIndex"), 
			function(t) {
				return [t.id, t];
			}
		));
		
		// decide how to "highlight" bars
		if( topicMapping[topic].selected ){//!== null){
			// previously selected topic
			this.prevHighlightColor = topicMapping[topic].color;
			colors[colors.indexOf(this.prevHighlightColor)] = HIGHLIGHT;
			this.gLayer = this.overlayLayer.selectAll( "g" )
				.attr("class", function(d,i) { return ["overlayGroup", this.colorClassPrefix + colors[i]].join(" ") }.bind(this) );
		} else {
			// add bar with offset
			this.useOffset = true;
		}
		for( var i = 0; i < termIndex.length; i++){
			var term = termIndex[i];
			if( topicals[i]> THRESHHOLD ){
				this.svgTermLabelLayer.selectAll("." + getTermClassTag(term))	
					.classed(this.colorClassPrefix + HIGHLIGHT, true)
				
				// highlight bars
				if( this.useOffset ) {
					// use the offset
					var offset = 0;
					if( this.totalOffsets.length > 0)
						offset = this.totalOffsets[i];
					
					this.svgTopicalBarLayer.selectAll("." + getTermClassTag(term))
						.classed(this.colorClassPrefix + HIGHLIGHT, true)
						.attr( "x2", this.line_length(offset + topicals[i]))
						.attr( "x1", this.line_length(offset));
				}
			}
		}
	}
};