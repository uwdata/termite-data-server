/*
	ViewParameters.js
	
	This file contains some final parameters for the view elements. 
	
	Parameters include:
		-defaults for different objects
		-functions to assign colors to events
		-functions to generate consistent class tags for objects based on term or topic
*/
//=====================================================================================
//									VIEW PARAMS
//=====================================================================================
// UPDATE: these are globals! What to do....maybe we can put in stateModel now that everyone can see it!

var THRESHHOLD = 0.01;
var HIGHLIGHT = "red";
var DEFAULT = "default";

/**
 * consistent d3 class labeling helper functions
 *
 * @param { string, int } term or topic to use in classname
 * @return { string } class name based on input
 */
function getTopicClassTag( topic ){
	return "__topic_" + sanitize(topic);
}
function getTermClassTag( term ){
	return "__term_" + sanitize(term);
}
function sanitize( text ){
	// Need to account for non-alphanumeric characters
	// Return a unique identifier for any input string
	return text.replace( /[^A-Za-z0-9]/g, "_" );
}
/** end class labeling helper functions **/
