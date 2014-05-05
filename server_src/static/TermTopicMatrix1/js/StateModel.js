var StateModel = Backbone.Model.extend({
	defaults : {
		"numAffinityTerms" : 50,
		"numSalientTerms" : 0,
		"visibleTerms" : [],
		"totalTerms" : 50,
		"sortType": "",
		"normColumns": true,
		"addTopTwenty": true,
		"highlightedTerm" : "",
		"highlightedTopic" : null,
		"doubleClickTopic": null,
		/**
		* Elements of topicIndex should be dicts containing:
		*   color : "default"
		*   id: an integer starting from 0 to numTopics-1
		*   name: a string
		*   position: an integer starting from 0 to numTopics-1
		*   selected: false
		**/
		"topicIndex": [],
		"version" : 0
	}
});

StateModel.prototype.initialize = function(options) {
	if (options.hasOwnProperty("url")) {
		this.url = options.url;
	}
	this.colorNames = ["orange", "blue", "green", "purple", "brown", "pink"];
	this.colorObjs = [];
	this.justAddedTerm = null;
	
	// initialize the colors
	for( var index = 0; index < this.colorNames.length; index++ ) {
		this.colorObjs.push({color: this.colorNames[index], usage: false});
	}
	
	// init topicIndex (temporaries!)
	/*var numTopics = 20;
	var topicObjectList = [];
	for( var i = 0; i < numTopics; i++){
		var topicObject = {};
		topicObject['id'] = i;
		topicObject['position'] = i;
		topicObject['name'] = "Topic " + i;
		topicObject['color'] = "DEFAULT";
		topicObject['selected'] = false;
		topicObjectList.push(topicObject);
	}
	//console.log(topicObjectList);
	this.set("topicIndex", topicObjectList);*/
};

StateModel.prototype.load = function() {
	var success = function(model, response, options) {
		console.log("Loaded StateModel", model, response, options);
		stateModel.batchClaimColors();
		stateModel.trigger("loaded:states");
	};
	var error = function(model, response, options) {
		console.log("Cannot load StateModel", model, response, options);
	};
	this.fetch({
		"success" : success,
		"error" : error
	})
};

/**
 * Returns the first free color if any. Marks returned color as used
 *
 * @private
 */
StateModel.prototype.getColor = function() {
	var color = DEFAULT;
	for( var index = 0; index < this.colorObjs.length; index++ ){
		if( !(this.colorObjs[index].usage) ){
			color = this.colorObjs[index].color;
			this.colorObjs[index].usage = true;
			break;
		}
	}
	return color;
}
/**
 * Marks the given color as usage:used if that color name exists
 * (used to reload state and free colors)
 *
 * @public
 * @param { string } name of color to be modified
 * @param { boolean } what to set usage to
 */
StateModel.prototype.colorUsage = function( color, used ) {
	if( color !== DEFAULT ){
		for( var index = 0; index < this.colorObjs.length; index++ ){
			if( color === this.colorObjs[index].color){
				this.colorObjs[index].usage = used;
				break;
			}
		}
	}
};

/**
 * runs through selected topics and claims all the colors
 * (used to restore state since colors are a derived property)
 * 
 * @public (technically, since loadStateFromDB is a global function)
 */
StateModel.prototype.batchClaimColors = function() {
	var selected = _.groupBy(this.get("topicIndex"), "selected")['true'];
	if( selected !== undefined ){
		for( var i in selected ){
			this.colorUsage( selected[i].color, true );
		}
	}
};

/**
 * Set user defined control feedback views
 *
 * @private
 * @this {state model}
 * @param { array } list of terms
 */
StateModel.prototype.setVisibleTerms = function ( userSpecifiedVisibleTerms ) {
	// get the new term by diff-ing lists
	var addedList = _.difference(userSpecifiedVisibleTerms, this.get("visibleTerms"));
	if( addedList.length === 0 )
		this.justAddedTerm = null;
	else
		this.justAddedTerm = addedList[0];
	//console.log("just added: ", this.justAddedTerm); 
	this.set( "visibleTerms", userSpecifiedVisibleTerms);
};

// helper function (no particular reason "justAddedTerm" can't be a default, I just don't like it)
/**
 * @public
 */
StateModel.prototype.getJustAddedTerm = function() {
	return this.justAddedTerm;
};

/** 
 * Handles click event: select one topic
 *
 * @this {state model}
 * @param { int } ID of clicked topic (not relative position)
 */
StateModel.prototype.selectTopic = function( topicId ) {
	// maps id to relative position (i.e. find where it is in the list by id)
	var topicMapping = _.object(_.map(this.get("topicIndex"), function(item){ return [item.id, item] }));

	var color = DEFAULT;
	// frees the color associated with the topic if the topic was already selected
	if( topicMapping[topicId].color !== DEFAULT ) {
		this.colorUsage( topicMapping[topicId].color, false );
		
		// update topicIndex
		this.get("topicIndex")[topicMapping[topicId].position].color = DEFAULT;
		this.get("topicIndex")[topicMapping[topicId].position].selected = false;
	}
	// assign a color to the selected topic if there are any free 
	else {
		color = this.getColor();
		
		if( color !== DEFAULT ) {
			console.log("topicIndex #" + topicId + " to color: " + color);
			// update topicIndex
			this.get("topicIndex")[topicMapping[topicId].position].color = color;
			this.get("topicIndex")[topicMapping[topicId].position].selected = true;
		}
	}
	//console.log(this.get("topicIndex"));
	// fire event to signify topic coloring may have changed
	this.trigger("color:topic", { "topic":topicId, "color": color } );
};

/**
 * Clears all topic selections (currently inefficiently implemented)
 * (called by "Clear all topic selections" user control button and loadStateFromDB)
 */
StateModel.prototype.clearAllSelectedTopics = function() {

	// deselect all the topics
	var topIndex = this.get("topicIndex");
	for( var i in topIndex ){
		if( topIndex[i].color !== DEFAULT ){
			this.colorUsage( topIndex[i].color, false );
			topIndex[i].color = DEFAULT;
			topIndex[i].selected = false;
			this.trigger("color:topic", {"topic":topIndex[i].id, "color": DEFAULT} );
		}
	}
	this.set("topicIndex", topIndex);
	this.trigger("clear:allTopics");
};

/** 
 * Handles sorting using double click on a topic label
 *
 * @this {state model}
 * @param { int } index of double clicked topic
 */
StateModel.prototype.getSortType = function ( topicIndex ){
	var sorts = ["desc", "asc", ""];
	
	if(this.get("doubleClickTopic") !== topicIndex)
		return sorts[0];
	else{
		var currentSort = this.get("sortType");
		var index = (sorts.indexOf(currentSort) + 1) % sorts.length;
		return sorts[index];
	}
};
StateModel.prototype.setDoubleClickTopic = function ( topicIndex ){
	var type = this.getSortType(topicIndex);
	if( type === "")
		this.set( "doubleClickTopic", null);
	else
		this.set( "doubleClickTopic", topicIndex);
	this.set( "sortType", type);
};
StateModel.prototype.clearSorting = function(){
	this.set( "doubleClickTopic", null);
	this.set( "sortType", "");
};
/** end double click event code **/

/**
 * Handles highlighting events triggered by mouseover and mouseout
 * 
 * @param { string } target term
 * @param { int } index of target topic
 */
StateModel.prototype.setHighlightedTerm = function( term ) {
	this.set("highlightedTerm", term );
};
StateModel.prototype.setHighlightedTopic = function( topic ) {
	this.set("highlightedTopic", topic );
};

/**
 * Updates the topic's label to the user defined label if the new label is different
 * 
 * @param { topicPosition } relative position of the topic to relabel
 * @param { topicLabel } new label to give the topic
 */
StateModel.prototype.updateLabel = function( topicPosition, topicLabel ){
	if( this.get("topicIndex")[topicPosition] !== topicLabel ){		
		// update topicIndex
		this.get("topicIndex")[topicPosition].name = topicLabel;
		this.trigger("change:topicLabels");
	}
};

/*** Topic Repositioning Stuff ***/
// TODO: change this functionality if we get drag and drop working
/** 
 * Changes topics' relative positions
 *
 * @param { topicSrc } original relative position of topic to move
 * @param { topicDest } new relative position of target topic
 */
StateModel.prototype.moveTopic = function( topicSrc, topicDest ){
	console.log("user wants to move topic " + topicSrc + " to " + topicDest);
	topicSrc = parseInt(topicSrc);
	topicDest = parseInt(topicDest);
	var topicIndex = this.get("topicIndex");
	if( topicSrc < topicDest ){		
		for( var i = topicSrc+1; i <= topicDest; i++){
			topicIndex[i].position = topicIndex[i].position-1;
		}
	}
	else if( topicSrc > topicDest ){		
		for( var i = topicDest; i < topicSrc; i++){
			topicIndex[i].position = topicIndex[i].position+1;
		}
	}
	topicIndex[topicSrc].position = topicDest;
	topicIndex.sort( function(a, b) { return a.position - b.position });
	console.log(topicIndex);
	this.trigger("change:topicPosition");
};

/** 
 * Resets the topics' positions to match their ids (i.e. 0, 1, 2, 3, ...)
 */
StateModel.prototype.originalPositions =  function(){
	var topicIndex = this.get("topicIndex");
	for( var i = 0; i < topicIndex.length; i++ ){
		topicIndex[i].position = topicIndex[i].id;
	}	
	topicIndex.sort( function(a, b) { return a.position - b.position });
	this.trigger("change:topicPosition");
};