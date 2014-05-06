/*
	SeriatedTermTopicProbabilityModel.js
	
	Currently: Reads in input file to get seriated terms, topics, term information 
		(e.g. saliency), and matrix of similarity values.
		
	
	Designed to take in a subset of the full list of terms, topics, and matrix. 
*/

var SeriatedTermTopicProbabilityModel = Backbone.Model.extend({
	defaults : {
		"matrix" : null,              /** @type{number[][]} **/
		"termIndex" : null,           /** @type{string[]}   A list of term texts. **/
		"topicIndex" : null,          /** @type{string[]}   A list of topic names. **/
		"sparseMatrix" : null,	// currently null
		"columnSums" : null,
		"topicMapping" : null         /** @type{integer[]}  A list of integers starting from 0 to numTopics - 1. **/
	}
});

SeriatedTermTopicProbabilityModel.prototype.initialize = function(options) {
	if (options.hasOwnProperty("url")) {
		this.url = options.url;
	}
	this.parentModel = null;
};

/**
 * Initialize seriated's parent model
 *
 * @private
 */
SeriatedTermTopicProbabilityModel.prototype.initModel = function ( fullModel ) {
	this.parentModel = filteredModel;
};

/**
 * Loads matrix, termIndex, and topicIndex from the model's "url"
 * and triggers a loaded event that the next model (child model) listens to.  
 * (This function is called after the state model loaded event is fired)
 *
 * @param { string } the location of datafile to load values from
 * @return { void }
 */
SeriatedTermTopicProbabilityModel.prototype.load = function () {
	var sumColumns = function(){
		var colSums = [];
		var matrix = this.get("matrix");
		for ( var i = 0; i < this.get("topicIndex").length; i++ ){
			var sum = 0.0;
			for( var j = 0; j < this.get("termIndex").length; j++){
				sum += matrix[j][i];
			}
			colSums.push(sum);
		}
		this.set("columnSums", colSums);
	}.bind(this);
	
	var successHandler = function(model, response, options) {
		console.log("Loaded SeriatedTermTopicProbabilityModel", model, response, options);
		// UDPATE: will get matrix, termIndex, topicIndex from stateModel
		sumColumns();
		this.printHTML('select#multi-select'); 	//TODO: hacky
		this.trigger("loaded:seriated");	
		
	}.bind(this);
	var errorHandler = function(model, response, options) {
		console.log("Cannot load SeriatedTermTopicProbabilityModel", model, response, options);
	}.bind(this);
	this.fetch({
		add : true,
		success : successHandler,
		error : errorHandler
	});	
};

/**
 * Prints out the html for multi-select options (i.e. all the terms available)
 *
 * @param { string } some identifier for the multi-select (e.g. class, div, id)
 */
// *** TODO: Find more efficient way to do this *** //
SeriatedTermTopicProbabilityModel.prototype.printHTML = function( target ) {
	var termIndex = this.get("termIndex").slice()
	termIndex.sort();
	for( var i = 0; i < termIndex.length; i++){
		$(target).append("<option>" + escape(termIndex[i]) + "</option>");
	}
	$(target).trigger('liszt:updated');
};
