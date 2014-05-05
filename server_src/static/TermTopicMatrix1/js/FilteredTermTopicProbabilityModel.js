/*
	FilteredTermTopicProbabilityModel.js
	
	This model is responsible for modifying data based on user inputs/controls 
		Current user control changes:
			-number of terms to show based on BEA choice order
			-number of terms to show based on saliency score (desc order)
			-specific terms to always show in the list of terms
			-whether or not to add top "twenty" terms of selected topics
			-sorting
	
	Details:
	--------
	Pulls data from SeriatedTermTopicProbabilityModel on initialize.
	Afterwards, this model is called when the user controls on the website are changed.
	At that time, the new "user defined" state is passed to the update function.  
*/

var FilteredTermTopicProbabilityModel = Backbone.Model.extend({
	defaults : {
		"matrix" : null,
		"termIndex" : null,
		"topicIndex" : null,
		"sparseMatrix" : null,
		"normalizedSparseMatrix": null,
		"termOrderMap": {},              /** A list of terms and their ordering **/
		"termRankMap": {},               /** A list of terms and their ranks    **/
		"termDistinctivenessMap" : {},   /** Term distinctiveness **/
		"termSaliencyMap": {}            /** Term saliency        **/
	}
});

FilteredTermTopicProbabilityModel.prototype.initialize = function(options) {
	if (options.hasOwnProperty("url")) {
		this.url = options.url;
	}
	this.stateModel = null;
	this.parentModel = null;
	
	// mappings
	this.termRankMap = null;
	this.termOrderMap = null;
	this.rowIndexMap = null;
	this.termDistinctivenessMap = null;
	this.termSaliencyList = [];
	
	// interaction related variables
	this.visibleTopTerms = {};
};


/**
 * Initialize filtered's parent and state model
 *
 * @private
 */
FilteredTermTopicProbabilityModel.prototype.initModel = function( model, state ){
	this.parentModel = model;
	this.stateModel = state;
};

/**
 * Loads various mappings from the model's "url"
 * and triggers a loaded event that the next model (child model) listens to.  
 * (This function is called after the seriated model loaded event is fired)
 *
 * @param { string } the location of datafile to load values from
 * @return { void }
 */
FilteredTermTopicProbabilityModel.prototype.load = function() {
	var initRowIndexMap = function( termIndex ){
		this.rowIndexMap = {};
		for ( var i = 0; i < termIndex.length; i++ ){
			this.rowIndexMap[termIndex[i]] = i;
		}
	}.bind(this);
	
	var initTermSaliencyList = function( saliencyMap ){
		termSaliencyList = [];
		tempList = [];
		for ( var term in saliencyMap ){
			tempList.push([term, saliencyMap[term]]);
		}
		tempList.sort(function(a, b) {return b[1] - a[1]});
		for( var i = 0; i < tempList.length; i++ ){
			this.termSaliencyList.push(tempList[i][0]);
		}
	}.bind(this);

	var successHandler = function(model, response, options) {
		console.log("Loaded FilteredTermTopicProbabilityModel", model, response, options);
		// initialize necessary maps, etc.
		this.termRankMap = response.termRankMap;
		this.termOrderMap = response.termOrderMap;
		this.termDistinctivenessMap = response.termDistinctivenessMap;
		initRowIndexMap( this.parentModel.get("termIndex") );
		initTermSaliencyList( response.termSaliencyMap );
		this.initTopTermLists();
		
		// filter initial data
		this.filter();
		this.trigger('loaded:filtered');
	}.bind(this);
	var errorHandler = function(model, response, options) {
		console.log("Cannot load FilteredTermTopicProbabilityModel", model, response, options);
	}.bind(this);
	this.fetch({
		add : false,
		success : successHandler,
		error : errorHandler
	});
};

/** 
 * Generates list of top twenty terms per topic in original topicIndex (called in load)
 *
 * @private
 */
FilteredTermTopicProbabilityModel.prototype.initTopTermLists = function() {
	var termIndex = this.parentModel.get("termIndex");
	var topicIndex = this.stateModel.get("topicIndex");
	
	var colFirstMatrix = generateColumnFirst(this.parentModel.get("matrix"));
	
	var termsPerTopic = 20;	
	this.topTermLists = {};
	for( var i = 0; i < topicIndex.length; i++){
		this.topTermLists[i] = [];
		
		// get term freqs for this topic
		var topicalFrequencies = colFirstMatrix[i];
		
		// sort the terms by topical frequency
		var indices = new Array(termIndex.length);
		for(var j = 0; j < termIndex.length; j++)
			indices[j] = j;
		indices.sort(function (a, b) { 
			return topicalFrequencies[a] < topicalFrequencies[b] ? 1 : topicalFrequencies[a] > topicalFrequencies[b] ? -1 : 0; 
		});

		// take the top 20 (unless there are fewer than 20)
		var count = 0;
		while(count < 20 && indices[count] > THRESHHOLD){
			this.topTermLists[i].push(termIndex[indices[count]]);
			count++;
		}
	}
};

/**
 * public update function (called in index.html)
 */
FilteredTermTopicProbabilityModel.prototype.update = function()
{
	this.filter();
};

/**
 * adds top twenty term list of selected topics to the visibleTopTerms list
 *
 * @private
 */
FilteredTermTopicProbabilityModel.prototype.addTopTerms = function() {
	var selected = _.groupBy(stateModel.get("topicIndex"), "selected")['true'];
	this.visibleTopTerms = {};
	for(var obj in selected){
		var topicObject = selected[obj];
		this.visibleTopTerms[topicObject.id] = this.topTermLists[topicObject.id];
	}
};

/**
 * Refreshes the termIndex and ordering based on user changes
 * 
 * @param { boolean } determines whether certain "set"s should trigger change events
 * @return { void }
 */
FilteredTermTopicProbabilityModel.prototype.filter = function( ) {
	var original_submatrix = this.parentModel.get("matrix");
	var original_termIndex = this.parentModel.get("termIndex");
	var original_topicIndex = this.parentModel.get("topicIndex");	// UPDATE: do we need the "original" index?
	
	var userDefinedTerms = this.stateModel.get("visibleTerms").slice(0);
	if(this.stateModel.get("addTopTwenty"))
		this.addTopTerms();
	else
		this.visibleTopTerms = {};
	
	var affinityLimit = this.stateModel.get("numAffinityTerms");
	var saliencyLimit = this.stateModel.get("numSalientTerms");
	
	var foundTerms = [];
	var subset = [];
	// choose terms to keep
	var chooseTerm = function( term ){
		if( userDefinedTerms.indexOf( term ) >= 0 ){
			foundTerms.push(term);
			return true;
		} 
		if( this.termRankMap[term] < affinityLimit ){
			return true;
		} 
		if( this.termSaliencyList.indexOf( term ) >= 0 && this.termSaliencyList.indexOf( term ) < saliencyLimit ){
			return true;
		}
		for(var topicNo in this.visibleTopTerms){
			if( this.visibleTopTerms[topicNo].indexOf( term ) >= 0 )
				return true;
		}
		return false;
	}.bind(this);
	
	// sort the terms
	var sortType = this.stateModel.get("sortType");
	for ( var i = 0; i < original_termIndex.length; i++ ){
		var term = original_termIndex[i];
		if( chooseTerm( term ) ){
			if(sortType === "")
				subset.push( [term, this.termOrderMap[ term ]] );
			else if( sortType === "desc") {
				var topic = this.stateModel.get("doubleClickTopic");
				subset.push( [term, 1 / (original_submatrix[this.rowIndexMap[term]][topic]*this.termDistinctivenessMap[term])]);
			}
			else if( sortType === "asc") {
				var topic = this.stateModel.get("doubleClickTopic");
				subset.push( [term, original_submatrix[this.rowIndexMap[term]][topic]*this.termDistinctivenessMap[term]]);
			}
		}
	}
	// find out which user defined terms were found in the dataset
	for( var i = 0; i < foundTerms.length; i++){
		userDefinedTerms.splice(userDefinedTerms.indexOf(foundTerms[i]),1);
	}
	subset.sort(function(a, b) {return a[1] - b[1]});
		
	// update model and state attributes
	matrix = [];
	termIndex = []
	for(var j = 0; j < subset.length; j++){
		var term = subset[j][0];
		termIndex.push(term);
		matrix.push(original_submatrix[this.rowIndexMap[term]]);
	}
	this.set("topicIndex", original_topicIndex); // UPDATE: necessary for global function sparseMatrix (idk why)
	this.set("termIndex", termIndex);
	this.set("matrix", matrix);
	this.set("normalizedSparseMatrix", generateSparseMatrix.bind(this)( this.parentModel.get("columnSums")));
	this.set("sparseMatrix", generateSparseMatrix.bind(this)( null ));

	this.stateModel.set("totalTerms", termIndex.length);
};