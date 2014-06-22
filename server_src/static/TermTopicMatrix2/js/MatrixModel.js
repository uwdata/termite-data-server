/**
 * @class MatrixModel
 * @classdesc MatrixModel stores all internal variables needed to represent a matrix visualization, including
 *   a sparse representation of the full matrix,
 *   a list of row elements,
 *   a list of column elements,
 *   the number of visible rows/columns,
 *   the range of matrix entry values under three matrix normalization schemes.
 *
 * @author Jason Chuang <jcchuang@cs.stanford.edu>
 * @param {Object} options The "options" object must contain an entry "options.state" of type "MatrixState".
 **/
var MatrixModel = CoreModel.extend({
	"defaults" : {
		"visibleRowDims" : 0,
		"visibleColumnDims" : 0,
		"visibleAnnotationDims" : 0,
		"visibleSelectionDims" : 0,
		
		"maxValue" : 0,					// @type {number} Cell statistics without normalization
		"maxRowValue" : 0,       		// @type {number} Cell statistics under row normalization
		"maxColumnValue" : 0,     		// @type {number} Cell statistics under column normalization
		
		"expansionColumnPosition" : undefined,
		"highlightSelectionIndex" : undefined,
		
		"vis:schedules" : undefined,
		"ui:dragActive" : false,
		"ui:dragData" : undefined,
		"ui:dragElement" : undefined,
		"ui:rowIndex" : 0,
		"ui:columnIndex" : 0,
		"ui:selectionIndex" : 0
	}
});

/**
 * Backbone-specific initialization routine.
 * @private
 **/
MatrixModel.prototype.initialize = function( options ) {
	CoreModel.prototype.initialize.call( this, options );
	this.state = options.state;
	this.__initStateEvents();
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.__initStateEvents = function() {
	this.__isUpdating = false;
	this.__pendingStateEvents = {};
	this.__currentStateEvents = {};
	this.__currentModelEvents = {};
	this.__rescheduleModelUpdates = _.debounce( this.__scheduleModelUpdates, 20 );
	this.listenTo( this.state, "dirty", this.__onStateEvents );
};

MatrixModel.prototype.__onStateEvents = function( dirty ) {
	this.__pendingStateEvents = this.__combineDirty__( this.__pendingStateEvents, dirty );
	this.__scheduleModelUpdates();
};

MatrixModel.prototype.__scheduleModelUpdates = function() {
	if ( this.__isUpdating )
		this.__rescheduleModelUpdates();
	this.__isUpdating = true;
	this.__currentStateEvents = this.__pendingStateEvents;
	this.__pendingStateEvents = {};
	this.__currentModelEvents = {};
	this.__updateModel();
	this.triggerDirty();
	this.__isUpdating = false;
};

MatrixModel.prototype.__isDirtyState = function() {
	var keys = Array.prototype.slice.call( arguments );
	return this.__isDirty__( this.__currentStateEvents, keys, 0 );
};

MatrixModel.prototype.__getDirtyState = function() {
	var keys = Array.prototype.slice.call( arguments );
	return this.__getDirty__( this.__currentStateEvents, keys, 0 );
};

MatrixModel.prototype.__isDirtyModel = function() {
	var keys = Array.prototype.slice.call( arguments );
	return this.__isDirty__( this.__currentModelEvents, keys, 0 );
};

MatrixModel.prototype.__setDirtyModel = function() {
	var keys = Array.prototype.slice.call( arguments );
	this.__currentModelEvents = this.__setDirty__( this.__currentModelEvents, keys, 0 );
};

MatrixModel.prototype.__getDirtyModel = function() {
	var keys = Array.prototype.slice.call( arguments );
	return this.__getDirty__( this.__currentModelEvents, keys, 0 );
};

MatrixModel.prototype.__setDirtyModelAndValue = function( key, value ) {
	this.set( key, value );
	this.__setDirtyModel( key );
};

MatrixModel.prototype.__setDirtyModelAndValues = function( keysAndValues ) {
	for ( var key in keysAndValues ) {
		var value = keysAndValues[ key ];
		this.set( key, value );
		this.__setDirtyModel( key );
	}
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.__updateModel = function() {
	this.__initEntries();
	this.__precomputeRelValues();
	this.__precomputeHighlights();
	this.__precomputeRankingsAndQuantiles();

	this.__updateSelections()
	this.__updateHighlights();
	this.__updateExpansions();
	this.__updateInclusionsAndExclusions();
	this.__updatePromotionsAndDemotions();
	
	this.__updateVisibilities();

	this.__updateRowAbsOrdering();
	this.__updateColumnAbsOrdering();
	this.__updateRowPositions();
	this.__updateColumnPositions();
	this.__updateEntryValues();
	this.__updateRowColumnValues();
	this.__updateCrossRefValues();
	this.__updateCrossRefPositionsAndSizes();

	this.__updateTexts();

	this.__updateRowMetas();
	this.__updateColumnMetas();
	this.__updateAnnotationControls();
	this.__updateSelectionGroups();

	this.__filterDataset();
	this.__scheduleVisTasks();
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.__entryIndexes = function( entryIndexes ) {
	if ( entryIndexes === true || entryIndexes === undefined )
		return _.keys( this.get( "hashEntries" ) );
	else
		return _.keys( entryIndexes );
};

MatrixModel.prototype.__rowIndexes = function( rowIndexes ) {
	if ( rowIndexes === true || rowIndexes === undefined )
		return _.range( this.get( "allRowElements" ).length );
	else
		return _.keys( rowIndexes ).map( function(d) { return parseInt(d) } );
};

MatrixModel.prototype.__columnIndexes = function( columnIndexes ) {
	if ( columnIndexes === true || columnIndexes === undefined )
		return _.range( this.get( "allColumnElements" ).length );
	else
		return _.keys( columnIndexes ).map( function(d) { return parseInt(d) } );
};

MatrixModel.prototype.__selectionIndexes = function( selectionIndexes ) {
	if ( selectionIndexes === true || selectionIndexes === undefined )
		return _.range( this.state.get( "selectionCount" ) );
	else
		return _.keys( selectionIndexes ).map( function(d) { return parseInt(d) } );
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.__updateColumnMetas = function() {
	var allColumnMetas = this.get( "allColumnMetas" );
	var columnExpansions = this.state.get( "columnExpansions" );
	for ( var t = 0; t < allColumnMetas.length; t++ ) {
		var meta = allColumnMetas[t];
		var wasVisible = ( meta.isVisible === true );
		var isVisible = ( columnExpansions.hasOwnProperty( t ) );
		meta.isEnter = ( !wasVisible && isVisible );
		meta.isStay = ( wasVisible && isVisible );
		meta.isExit = ( wasVisible && !isVisible );
		if ( isVisible !== meta.isVisible ) {
			meta.isVisible = isVisible;
			this.setDirty( "allColumnMetas", meta.key, "isVisible" );
			this.__setDirtyModel( "allColumnMetas", "isVisible" );
		}
	}
	this.__setDirtyModel( "allColumnMetas", [ "isEnter", "isStay", "isExit" ] );
};

MatrixModel.prototype.__updateRowMetas = function() {
	var allRowMetas = this.get( "allRowMetas" );
	for ( var s = 0; s < allRowMetas.length; s++ ) {
		var meta = allRowMetas[s];
		meta.isEnter = false;
		meta.isStay = false;
		meta.isExit = false;
		if ( false !== meta.isVisible ) {
			meta.isVisible = false;
			this.setDirty( "allRowMetas", meta.key, "isVisible" );
			this.__setDirtyModel( "allRowMetas", "isVisible" );
		}
	}
	this.__setDirtyModel( "allRowMetas", [ "isEnter", "isStay", "isExit" ] );
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.__filterDataset = function() {
	if ( this.getDirty() === true ) {
		this.__setDirtyModelAndValues({
			"visibleEntries" : undefined,
			"visibleRowElements" : undefined,
			"visibleColumnElements" : undefined,
			"visibleRowCrossRefs" : undefined,
			"visibleColumnCrossRefs" : undefined,
			"visibleAnnotationControls" : undefined,
			"visibleRowMetas" : undefined,
			"visibleColumnMetas" : undefined
		});
	}

	var allEntries = this.get( "allEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );
	var allRowCrossRefs = this.get( "allRowCrossRefs" );
	var allColumnCrossRefs = this.get( "allColumnCrossRefs" );
	var allAnnotationControls = this.get( "allAnnotationControls" );
	var allRowMetas = this.get( "allRowMetas" );
	var allColumnMetas = this.get( "allColumnMetas" );

	var newEntries = _.filter( allEntries, function(d) { return d.isEnter } );
	var newRowElements = _.filter( allRowElements, function(d) { return d.isEnter } );
	var newColumnElements = _.filter( allColumnElements, function(d) { return d.isEnter } );
	var newRowCrossRefs = _.filter( allRowCrossRefs, function(d) { return d.isEnter } );
	var newColumnCrossRefs = _.filter( allColumnCrossRefs, function(d) { return d.isEnter } );
	var newAnnotationControls = _.filter( allAnnotationControls, function(d) { return d.isEnter } );
	var newRowMetas = _.filter( allRowMetas, function(d) { return d.isEnter } );
	var newColumnMetas = _.filter( allColumnMetas, function(d) { return d.isEnter } );
	
	var transitionEntries = ( this.get( "visibleEntries" ) || [] ).concat( newEntries );
	var transitionRowElements = ( this.get( "visibleRowElements" ) || [] ).concat( newRowElements );
	var transitionColumnElements = ( this.get( "visibleColumnElements" ) || [] ).concat( newColumnElements );
	var transitionRowCrossRefs = ( this.get( "visibleRowCrossRefs" ) || [] ).concat( newRowCrossRefs );
	var transitionColumnCrossRefs = ( this.get( "visibleColumnCrossRefs" ) || [] ).concat( newColumnCrossRefs );
	var transitionAnnotationControls = ( this.get( "visibleAnnotationControls" ) || [] ).concat( newAnnotationControls );
	var transitionRowMetas = ( this.get( "visibleRowMetas" ) || [] ).concat( newRowMetas );
	var transitionColumnMetas = ( this.get( "visibleColumnMetas" ) || [] ).concat( newColumnMetas );
	
	var visibleEntries = _.reject( transitionEntries, function(d) { return d.isExit } );
	var visibleRowElements = _.reject( transitionRowElements, function(d) { return d.isExit } );
	var visibleColumnElements = _.reject( transitionColumnElements, function(d) { return d.isExit } );
	var visibleRowCrossRefs = _.reject( transitionRowCrossRefs, function(d) { return d.isExit } );
	var visibleColumnCrossRefs = _.reject( transitionColumnCrossRefs, function(d) { return d.isExit } );
	var visibleAnnotationControls = _.reject( transitionAnnotationControls, function(d) { return d.isExit } );
	var visibleRowMetas = _.reject( transitionRowMetas, function(d) { return d.isExit } );
	var visibleColumnMetas = _.reject( transitionColumnMetas, function(d) { return d.isExit } );

	this.__setDirtyModelAndValues({
		"visibleEntries" : visibleEntries,
		"visibleRowElements" : visibleRowElements,
		"visibleColumnElements" : visibleColumnElements,
		"visibleRowCrossRefs" : visibleRowCrossRefs,
		"visibleColumnCrossRefs" : visibleColumnCrossRefs,
		"visibleAnnotationControls" : visibleAnnotationControls,
		"visibleRowMetas" : visibleRowMetas,
		"visibleColumnMetas" : visibleColumnMetas,
		"transitionEntries" : transitionEntries,
		"transitionRowElements" : transitionRowElements,
		"transitionColumnElements" : transitionColumnElements,
		"transitionRowCrossRefs" : transitionRowCrossRefs,
		"transitionColumnCrossRefs" : transitionColumnCrossRefs,
		"transitionAnnotationControls" : transitionAnnotationControls,
		"transitionRowMetas" : transitionRowMetas,
		"transitionColumnMetas" : transitionColumnMetas
	});

	var visibleRowDims = visibleRowElements.length;
	var visibleColumnDims = visibleColumnElements.length;
	var visibleAnnotationDims = visibleAnnotationControls.length;

	if ( visibleRowDims !== this.get( "visibleRowDims" ) ) {
		this.set( "visibleRowDims", visibleRowDims );
		this.setDirty( "visibleRowDims" );
	}
	if ( visibleColumnDims !== this.get( "visibleColumnDims" ) ) {
		this.set( "visibleColumnDims", visibleColumnDims );
		this.setDirty( "visibleColumnDims" );
	}
	if ( visibleAnnotationDims !== this.get( "visibleAnnotationDims" ) ) {
		this.set( "visibleAnnotationDims", visibleAnnotationDims );
		this.setDirty( "visibleAnnotationDims" );
	}
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.RESIZE_DURATION = 180;
MatrixModel.prototype.STANDARD_SCHEDULE = (function() {
	var standardExit  = { delay : -525, duration : 300, ease : "cubic-in-out" };
	var standardStay  = { delay : -200, duration : 400, ease : "cubic-in-out" };
	var standardEnter = { delay :  225, duration : 300, ease : "cubic-in-out" };
	return {
		"enter" : standardEnter,
		"stay"  : standardStay,
		"exit"  : standardExit
	};
})();
MatrixModel.prototype.ADDITIONAL_SCHEDULES = (function() {
	var earlyExit     = { delay : -570, duration : 180, ease : "cubic-in" };
	var standardStay  = { delay : -300, duration : 600, ease : "cubic-in-out" };
	var lateEnter     = { delay :  450, duration : 180, ease : "cubic-in" };
	return {
/*
		"transitionAnnotationControls" : {
			"enter" : lateEnter,
			"stay"  : standardStay,
			"exit"  : earlyExit
		},
		"transitionColumnMetas" : {
			"enter" : lateEnter,
			"stay"  : standardStay,
			"exit"  : earlyExit
		}		
*/
	};
})();

MatrixModel.prototype.__scheduleVisTasks = function() {
	var elementIDs = [
		"allEntries",
		"allRowElements", "allColumnElements",
		"allRowCrossRefs", "allColumnCrossRefs",
		"allRowMetas", "allColumnMetas",
		"allAnnotationControls"
	];
	var allSchedules = [];
	var visSchedules = {};
	for ( var i = 0; i < elementIDs.length; i++ ) {
		var elementID = elementIDs[i].replace( /^all/, "transition" );
		var element = this.get( elementID );
		var isEnter = _.some( element, someEnters );
		var isStay = _.some( element, someStays );
		var isExit = _.some( element, someExits );
		var visSchedule = {
			"isEnter" : isEnter,
			"isStay" : isStay,
			"isExit" : isExit
		};
		var schedule;
		if ( isEnter ) {
			if ( this.ADDITIONAL_SCHEDULES.hasOwnProperty( elementID ) )
				schedule = _.clone( this.ADDITIONAL_SCHEDULES[ elementID ][ "enter" ] );
			else
				schedule = _.clone( this.STANDARD_SCHEDULE[ "enter" ] );
			visSchedule[ "enter" ] = schedule;
			allSchedules.push( schedule );
		}
		if ( isStay ) {
			if ( this.ADDITIONAL_SCHEDULES.hasOwnProperty( elementID ) )
				schedule = _.clone( this.ADDITIONAL_SCHEDULES[ elementID ][ "stay" ] );
			else
				schedule = _.clone( this.STANDARD_SCHEDULE[ "stay" ] );
//			if ( ! this.__isDirtyModel( elementIDs[i], [ "rowPosition", "columnPosition", "value" ] ) )
//				schedule.duration = 0.0;
			visSchedule[ "stay" ] = schedule;
			allSchedules.push( schedule );
		}
		if ( isExit ) {
			if ( this.ADDITIONAL_SCHEDULES.hasOwnProperty( elementID ) )
				schedule = _.clone( this.ADDITIONAL_SCHEDULES[ elementID ][ "exit" ] );
			else
				schedule = _.clone( this.STANDARD_SCHEDULE[ "exit" ] );
			visSchedule[ "exit" ] = schedule;
			allSchedules.push( schedule );
		}
		visSchedules[ elementID ] = visSchedule;
	}
	var minStartTime = undefined;
	var maxEndTime = undefined;
	for ( var i = 0; i < allSchedules.length; i++ ) {
		var schedule = allSchedules[ i ];
		var startTime = schedule.delay;
		var endTime = schedule.delay + schedule.duration;
		minStartTime = Math.min( minStartTime || 0, startTime );
		maxEndTime = Math.max( maxEndTime || 0, endTime );
	}
	minStartTime || ( minStartTime = 0 );
	maxEndTime || ( maxEndTime = 0 );
	for ( var i = 0; i < allSchedules.length; i++ ) {
		var schedule = allSchedules[ i ];
		schedule.delay -= minStartTime;
	}
	var totalDuration = maxEndTime - minStartTime;
	visSchedules[ "duration" ] = totalDuration;
	visSchedules[ "vis" ] = {
		"pre" : {
			"delay" : 0,
			"duration" : this.RESIZE_DURATION,
			"ease" : "cubic-in-out"
		},
		"post" : {
			"delay" : totalDuration - this.RESIZE_DURATION,
			"duration" : this.RESIZE_DURATION,
			"ease" : "cubic-in-out"
		}
	};
	this.set( "vis:schedules", visSchedules );
	function someEnters( d ) { return d.isEnter }
	function someStays( d ) { return d.isStay }
	function someExits( d ) { return d.isExit }
};

//--------------------------------------------------------------------------------------------------
// Compatibility with Node.js

if ( typeof module !== "undefined" ) {
	module.exports = MatrixModel;
}
