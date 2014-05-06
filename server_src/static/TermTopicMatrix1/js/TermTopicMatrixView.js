/*
	TermTopicMatrixView.js
	
	This view is responsible for generating the term:topic similarity matrix.
	
	Details:
	--------
	Pulls list of ordered terms, topics, and similarity values from 
	FilteredTermTopicProbabilityModel. 
	
	Additionally, uses parameters defined in ViewParameters.js.
*/
var MATRIX_CONTAINER_PADDING = {
	left_separation: 8,
	top_separation: 12,
	left: 110,
	right: 20,
	top: 60,
	bottom: 60,
	fullWidth : function( numTopics ) { return this.left + this.right + MATRIX_ENCODING_PARAMETERS.packing() * numTopics },
	fullHeight : function( numTopics, numTerms ) { return this.top + this.bottom + MATRIX_ENCODING_PARAMETERS.packing() * numTerms }
};
	
var MATRIX_ENCODING_PARAMETERS = {
	NUM_TOPICS : 0,
	NUM_TERMS : 0,
	MATRIX : null,
	setNumTopics : function(numTopics) { this.NUM_TOPICS = numTopics; },
	setNumTerms : function(numTerms) { this.NUM_TERMS = numTerms; },
	setMatrix : function(matrix) { this.MATRIX = matrix; },
	DENSE_NUM_TOPICS: 50,
	LOOSE_NUM_TOPICS: 20,
	DENSE_PACKING: 12,
	LOOSE_PACKING: 18,
	packing : function()
	{
		return 12;
	},
	TARGET_PIXEL_DENSITY : 0.20,
	radius : function( sparseMatrix, normalizedSparseMatrix, numTopics, numTerms )	// matrix view
	{
		// calculate non-normalized scale
		var totalCirclePixels = 0.0;
		for ( var i in sparseMatrix )
			totalCirclePixels += sparseMatrix[i].value * Math.PI;
		//console.log("total pixels = " + totalCirclePixels);
		// Add up # pixels:  prob * Math.PI;
		var totalMatrixPixels = numTopics * numTerms * this.packing() * this.packing();
		//console.log("total matrix pixels = " + totalMatrixPixels);

		var targetPixels = ( totalMatrixPixels * this.TARGET_PIXEL_DENSITY );
		//console.log("target matrix pixels = " + targetPixels);
		var observedPixels = totalCirclePixels;
		var areaScale = targetPixels / observedPixels;
		var radiusScale = Math.sqrt( areaScale );
		
		//var totalCirclePixels = 0.0;
		//for ( var i in sparseMatrix )
		//	totalCirclePixels += radiusScale * radiusScale * ( sparseMatrix[i].value ) * Math.PI;
			
		// calculate normalized scale
		var normTotalCirclePixels = 0.0;
		for ( var i in normalizedSparseMatrix )
			normTotalCirclePixels += normalizedSparseMatrix[i].value * Math.PI;
		//console.log("norm total pixels = " + normTotalCirclePixels);
		var normRadiusScale = Math.sqrt( targetPixels / normTotalCirclePixels );
		
		return { rs: radiusScale, nrs: normRadiusScale };
	}
};

var TermTopicMatrixView = Backbone.View.extend({
	initialize : function() {
		this.parentModel = null;
		this.stateModel = null;
		
		// encodings
		this.xs = null;
		this.ys = null;
		this.rs = null;
		this.normRs = null;
		
		// svg layers
		this.svg = null;
		this.xGridlineLayer = null;
		this.yGridlineLayer = null;
		this.matrixLayer = null;
		this.leftLabelLayer = null;
		this.topLabelLayer = null;
		this.sortDescriptionLayer = null;
				
		// interaction variables
		this.colorCache = [];
		this.normalColor = "normal";
		
		this.highlightedTerm = null;
		this.highlightedTopic = null;	
		this.lastTransitionedTerm = null;	
	}
});
/** 
 * Initialize matrix view's parent model
 *
 * @private
 */
TermTopicMatrixView.prototype.initModel = function( model, state ) {
	this.parentModel = model;
	this.stateModel = state;
};

/** 
 * Initialize/render matrix view's elements for the first time
 *
 * @private
 */
TermTopicMatrixView.prototype.load = function(){
	this.initialSelection();
	this.renderInit();
	this.renderUpdate();
	
	// tell view to color the selected topics
	var selected = _.groupBy(this.stateModel.get("topicIndex"), "selected")['true'];
	if( selected !== undefined ){
		for( var i = 0; i < selected.length; i++ ){
			this.selectTopic(selected[i].id, selected[i].color);
		}
	}
};

/** 
 * Initialize color cache from stateModel (called by renderInit only)
 *
 * @private
 */
TermTopicMatrixView.prototype.initialSelection = function(){
	var topicIndex = this.stateModel.get("topicIndex");
	for( var i = 0; i < topicIndex.length; i++ ){
		this.colorCache[i] = topicIndex[i].color;
	}
};

/** 
 * Initialize matrix view's elements
 *	-svg layers
 *	-encoders
 *  -etc.
 *
 * @private
 */
TermTopicMatrixView.prototype.renderInit = function(){
	var matrix = this.parentModel.get("sparseMatrix");
	var normalizedMatrix = this.parentModel.get("normalizedSparseMatrix")
	var termIndex = this.parentModel.get("termIndex");
	var topicIndex= this.stateModel.get("topicIndex");
				
	this.xs = d3.scale.linear();
	this.ys = d3.scale.linear();

	var radScales = MATRIX_ENCODING_PARAMETERS.radius( matrix, normalizedMatrix, topicIndex.length, termIndex.length );

	this.rs = d3.scale.sqrt()
		.domain( [ 0, 1 ] )
		.range( [ 0, radScales.rs ] );
		
	this.normRs = d3.scale.sqrt()
		.domain( [ 0, 1 ] )
		.range( [ 0, radScales.nrs ] );
	
	var container = d3.select( this.el );
	this.svg = container.append( "svg:svg" )
	
	this.initMatrixView();
	this.initTopLabelView();
	this.initLeftLabelView();
};

/** 
 * Update matrix view's elements based on parent model's termIndex, topicIndex, and matrix
 *
 * @private
 */
TermTopicMatrixView.prototype.renderUpdate = function( options ){
	
	var termIndex = this.parentModel.get("termIndex");
	var topicIndex= this.stateModel.get("topicIndex");
	
	this.xs
		.domain( [ 0, topicIndex.length ] )
		.range( [ MATRIX_CONTAINER_PADDING.left, MATRIX_CONTAINER_PADDING.left + topicIndex.length * MATRIX_ENCODING_PARAMETERS.packing() ] );
	this.ys
		.domain( [ 0, termIndex.length ] )
		.range( [ MATRIX_CONTAINER_PADDING.top, MATRIX_CONTAINER_PADDING.top + termIndex.length * MATRIX_ENCODING_PARAMETERS.packing() ] );
	this.svg
		.style( "width", MATRIX_CONTAINER_PADDING.fullWidth( topicIndex.length ) + "px" )
		.style( "height", MATRIX_CONTAINER_PADDING.fullHeight( topicIndex.length, termIndex.length ) + "px" )
	
	this.updateMatrixView();
	this.updateTopLabelView();
	this.updateLeftLabelView();
	this.transitionUserAddedTerm();
};


// UPDATE: init and update functions that need topic/topicIndex need to change to new
// naming and attribute convention
/** 
 * Init and update functions for each layer
 *
 * @private
 */
TermTopicMatrixView.prototype.initMatrixView = function(){			
	this.xGridlineLayer = this.svg.append( "svg:g" ).attr( "class", "xGridlineLayer" );
	this.yGridlineLayer = this.svg.append( "svg:g" ).attr( "class", "yGridlineLayer" );
	this.matrixLayer = this.svg.append( "svg:g" ).attr( "class", "matrixLayer" );
};
TermTopicMatrixView.prototype.updateMatrixView = function(){
	var normColumns = this.stateModel.get("normColumns");
	var matrix = this.parentModel.get("sparseMatrix");
	var normMatrix = this.parentModel.get("normalizedSparseMatrix");
	var termIndex = this.parentModel.get("termIndex");

	var topicIndex= this.stateModel.get("topicIndex");
	var topicMapping = _.object(_.map(this.stateModel.get("topicIndex"), function(item){ return [item.id, item] }));
	//d.topicIndex === topic id

	if( normColumns )
		matrix = normMatrix;
	
	this.matrixLayer.selectAll( "circle" ).data( matrix ).exit().remove();
	this.matrixLayer.selectAll( "circle" ).data( matrix ).enter().append( "svg:circle" )
		.on( "mouseout", function() { this.trigger( "mouseout:term", ""); this.trigger( "mouseout:topic", null); }.bind(this) )
	this.matrixLayer.selectAll( "circle" ).data( matrix )	
		.attr( "class", function(d) { return [ "matrixElement", this.colorMap(topicMapping[d.topicIndex].color), getTopicClassTag(d.topicIndex.toString()), getTermClassTag(d.term) ].join(" ") }.bind(this))
		.on( "mouseover", function(d) { this.trigger( "mouseover:term", d.term); this.trigger( "mouseover:topic", d.topicIndex); }.bind(this) )
		.on( "click", function (d) { this.trigger( "click:topic", d.topicIndex ) }.bind(this)) 
		.attr( "cx", function(d) { return this.xs(topicMapping[d.topicIndex].position+0.5) }.bind(this) )
		.attr( "cy", function(d) { return this.ys(d.termIndex+0.5) }.bind(this) )
		.attr( "r", function(d) { 
			if( normColumns )
				return this.normRs(d.value)
			else
				return this.rs(d.value) 
		}.bind(this) )
		
	this.xGridlineLayer.selectAll( "line" ).data( termIndex ).exit().remove();
	this.xGridlineLayer.selectAll( "line" ).data( termIndex ).enter().append( "svg:line" )
		.attr( "x1", this.xs(0.5) )
	this.xGridlineLayer.selectAll( "line" ).data( termIndex )
		.attr( "class", function(d) { return [ "verticalLine", this.normalColor, getTermClassTag(d) ].join(" ") }.bind(this)) 
		.attr( "x2", this.xs(topicIndex.length-0.5) )
		.attr( "y1", function(d,i) { return this.ys(i+0.5) }.bind(this) )
		.attr( "y2", function(d,i) { return this.ys(i+0.5) }.bind(this) )

	this.yGridlineLayer.selectAll( "line" ).data( topicIndex ).exit().remove();
	this.yGridlineLayer.selectAll( "line" ).data( topicIndex ).enter().append( "svg:line" )
		.attr( "y1", this.ys(0.5) )
	this.yGridlineLayer.selectAll( "line" ).data( topicIndex )
		.attr( "class", function(d, i) { return [ "verticalLine", this.colorMap(d.color), getTopicClassTag(d.id.toString())].join(" ") }.bind(this)) 
		.attr( "x1", function(d,i){ return this.xs(i+0.5) }.bind(this) )
		.attr( "x2", function(d,i){ return this.xs(i+0.5) }.bind(this) )
		.attr( "y2", this.ys(termIndex.length-0.5) )
};
TermTopicMatrixView.prototype.initTopLabelView = function(){
	this.topLabelLayer = this.svg.append( "svg:g" )
		.attr( "class", "topLabelLayer" );
	this.sortDescriptionLayer = this.svg.append( "svg:g" )
		.attr( "class", "sortDescriptionLayer" );		
};


TermTopicMatrixView.prototype.colorMap = function(colorname){
	if(colorname === DEFAULT)
		return this.normalColor;
	return colorname;
};


TermTopicMatrixView.prototype.updateTopLabelView = function(){
	var topicIndex= this.stateModel.get("topicIndex");

	var dblclickTimer = null;

	this.sortDescriptionLayer.selectAll( "text" ).data( topicIndex ).exit().remove()
	this.sortDescriptionLayer.selectAll( "text" ).data( topicIndex ).enter().append( "svg:text" )
		.on( "mouseout", function() { this.trigger( "mouseout:topic", null) }.bind(this))
		.attr( "y", 10 )
	this.sortDescriptionLayer.selectAll( "text" ).data( topicIndex )
		.attr( "class", function(d, i) { return ["sortDescription", this.colorMap(d.color), getTopicClassTag((d.id).toString())].join(" ")}.bind(this))//return ["topLabel", this.colorCache[i], getTopicClassTag(d)].join(" ") }.bind(this))
		.on( "mouseover", function(d, i) { this.trigger( "mouseover:topic", d.id ) }.bind(this))
		.attr( "transform", function(d, i) { return "translate(" + this.xs(i+0.5) + "," + (this.ys(0)-MATRIX_CONTAINER_PADDING.top_separation) + ")" }.bind(this) )
		.text( function(d,i) {
			if( this.stateModel.get("doubleClickTopic") === d.id){
				if(this.stateModel.get("sortType") === "asc")
					return "\u2b06 ";
				else if (this.stateModel.get("sortType") === "desc")
					return "\u2b07 ";
			}}.bind(this));
			
	this.topLabelLayer.selectAll( "text" ).data( topicIndex ).exit().remove()
	this.topLabelLayer.selectAll( "text" ).data( topicIndex ).enter().append( "svg:text" )
		.on( "mouseout", function() { this.trigger( "mouseout:topic", null) }.bind(this))
		.attr( "y", 3 )
	this.topLabelLayer.selectAll( "text" ).data( topicIndex )
		.attr( "class", function(d, i) { return ["toplabel", this.colorMap(d.color), getTopicClassTag((d.id).toString())].join(" ")}.bind(this))//return ["topLabel", this.colorCache[i], getTopicClassTag(d)].join(" ") }.bind(this))
		.on( "mouseover", function(d, i) { this.trigger( "mouseover:topic", d.id ) }.bind(this))
		.attr( "transform", function(d, i) { return "translate(" + this.xs(i+0.5) + "," + (this.ys(0)-MATRIX_CONTAINER_PADDING.top_separation) + ") rotate(295)" }.bind(this) )
		.text( function(d, i) { return d.name; })
		.on( "click", function(d, i) { 
				dblclickTimer = setTimeout(function(){ clickWork(d, i)}, 200);
			})
		.on( "dblclick", function(d, i){ 
				clearTimeout(dblclickTimer);
  				dblclickTimer = null;
  				this.trigger( "doubleClick:topic", d.id) 
  			}.bind(this)) 	
  	
  	var clickWork = function(d, i) {
  		if(dblclickTimer === null)
			return; 
		else { 
			this.trigger( "click:topic", d.id)
		}
  	}.bind(this);  	
};

TermTopicMatrixView.prototype.initLeftLabelView = function(){
	this.leftLabelLayer = this.svg.append( "svg:g" )
		.attr( "class", "leftLabelLayer" );
};
TermTopicMatrixView.prototype.updateLeftLabelView = function(){
	var termIndex = this.parentModel.get("termIndex");
	
	this.leftLabelLayer.selectAll( "text" ).data( termIndex ).exit().remove();
	this.leftLabelLayer.selectAll( "text" ).data( termIndex ).enter().append( "svg:text" )
		.on( "mouseout", function() { this.trigger( "mouseout:term", "") }.bind(this))
		.attr( "y", 3 )
	this.leftLabelLayer.selectAll( "text" ).data( termIndex )
		.attr( "class", function(d) { return ["leftLabel", this.normalColor, getTermClassTag(d)].join(" ") }.bind(this))
		.on( "mouseover", function(d) { this.trigger( "mouseover:term", d ) }.bind(this))
		.attr( "transform", function(d,i) { return "translate(" + (this.xs(0)-MATRIX_CONTAINER_PADDING.left_separation) + "," + this.ys(i+0.5) + ")" }.bind(this) )
		.text( function(d) { return d } )
};


TermTopicMatrixView.prototype.transitionUserAddedTerm = function() {
	var addedTerm = this.stateModel.getJustAddedTerm();
	if( addedTerm !== null && this.lastTransitionedTerm !== addedTerm ){
		console.log("matrix transitioning ", getTermClassTag(addedTerm));
		console.log(this.svg.selectAll("." + getTermClassTag(addedTerm)));
		d3.selectAll("." + getTermClassTag(addedTerm)).transition().duration(1000).style("fill", "red").style("stroke", "red");
		// TODO: transition out is too fast
		setTimeout(function() {	
			console.log("here");
			d3.selectAll("." + getTermClassTag(addedTerm)).transition().duration(2000).style("fill", "").style("stroke", "");
		}, 1500)
		this.lastTransitionedTerm = addedTerm;
	}
};
/** end init and update functions **/

/** 
 * Updates the view (public encapsulation used in index.html)
 */
TermTopicMatrixView.prototype.update = function( options ) {
	this.renderUpdate();
};


// Interactions
/** 
 * Calls appropriate functions to deal with term highlight event elements
 *
 * @param { model } model is passed but unused
 * @param { string } value is the target term
 * @return { void }
 */
TermTopicMatrixView.prototype.onSelectionTermChanged = function( model, value ) {
	var term = value;
	if(term === "")
		this.unhighlight( true, false );
	else
		this.highlight( term, null );
};
/** 
 * Calls appropriate functions to deal with topic highlight event elements
 *
 * @param { model } model is passed but unused
 * @param { int } value is the target topic index
 * @return { void }
 */
TermTopicMatrixView.prototype.onSelectionTopicChanged =  function( model, value ) {
	var topic = value;
	if(topic === null)
		this.unhighlight( false, true );
	else
		this.highlight( null, topic );
};

/** 
 * Highlights elements based on term and/or topic
 *
 * @private
 */
TermTopicMatrixView.prototype.highlight = function( term, topicId ) {
	if( term !== null ){
		this.highlightedTerm = term;
		this.svg.selectAll("." + getTermClassTag(term))
			.classed(HIGHLIGHT, true)
	} 
	
	if( topicId !== null ){
		var termIndex = this.parentModel.get("termIndex");
		var matrix = this.parentModel.get("matrix");
		
		this.highlightedTopic = topicId;
		this.svg.selectAll("." + getTopicClassTag(topicId.toString()))
			.classed(HIGHLIGHT, true)	
			
		// highlight term labels
		for( var i = 0; i < termIndex.length; i++){
			var term = termIndex[i];
			if( matrix[i][topicId] > THRESHHOLD ){
				this.leftLabelLayer.selectAll("." + getTermClassTag(term))	
					.classed(HIGHLIGHT, true)
			}
		}
	}
};
/** 
 * Unhighlights elements based on term and/or topic
 *
 * @private
 */
TermTopicMatrixView.prototype.unhighlight = function( term, topic ) {
	if( term  && this.highlightedTerm !== null){
		this.svg.selectAll("." + getTermClassTag(this.highlightedTerm))
			.classed(HIGHLIGHT, false)
		
		this.highlightedTerm = null;
	} 
	
	if( topic && this.hightlightedTopic !== null){
		var termIndex = this.parentModel.get("termIndex");
		var matrix = this.parentModel.get("matrix");
		
		var topicNo = this.highlightedTopic;
		this.svg.selectAll("." + getTopicClassTag(topicNo.toString()))
			.classed(HIGHLIGHT, false)
		
		// unhighlight labels
		for( var i = 0; i < termIndex.length; i++){
			var term = termIndex[i];
			if( matrix[i][topicNo] > THRESHHOLD ){
				this.leftLabelLayer.selectAll("." + getTermClassTag(term))	
					.classed(HIGHLIGHT, false)
			}
		}
		
		this.highlightedTopic = null;
	}
};

// UPDATE: handler for selections, update how this works? should be able to pull from stateModel
// but how to get "updates" vs. already colored (maybe do a check in selectTopic, is this going to add
// too much overhead?)
/** 
 * Calls appropriate functions to deal with topic selection event elements
 *
 * @param { object } either 1. object of (topic, color) or
 *							2. object of ALL changed attributes
 * @return { void }
 */
var somethingsomething  = null;
TermTopicMatrixView.prototype.updateColors = function( options ) {
	somethingsomething = options;
	if( options !== undefined && options !== null ){
		// check for "changed" object
		if( options.changed !== undefined && options.changed !== null && options.changed.topicIndex !== undefined ){
			var selected = _.groupBy(this.stateModel.get("topicIndex"), "selected")['true'];
			if( selected !== undefined ){
				for( var i = 0; i < selected.length; i++ ) {
					this.selectTopic( selected[i].id, selected[i].color );
				}
			}
		}
		// else this is updating a singe topic
		else if( options.topic !== undefined ){
			this.selectTopic( options.topic, options.color );
		}
	}
}

/** 
 * topic selection behavior
 *
 * @private
 */
TermTopicMatrixView.prototype.selectTopic = function( topicId , colorClass ) {	
	if( topicId !== null){

		if( colorClass === DEFAULT )
			colorClass = this.normalColor;
			
		var oldColor = this.colorCache[topicId];

		// set new color
		this.svg.selectAll("." + getTopicClassTag(topicId.toString()))
			.classed(oldColor, false)
			.classed(colorClass, true)
			
		this.colorCache[topicId] = colorClass;
	}
};