/**
 * @class MatrixState
 * @classdesc MatrixState contains all variables needed to create/reconstruct the state of a matrix including
 *   an identifier for the current dataset,
 *   the visibilities of rows and columns,
 *   the ordering of rows and columns,
 *   the selections of rows and columns,
 *   highlighting of rows and columns.
 *   a list of row lables,
 *   a list of column labels, and
 *   a list of selection descriptions.
 *
 * @author Jason Chuang <jcchuang@cs.stanford.edu>
 */
var MatrixState = CoreModel.extend({
	// The following list of default values are initialized in the code.
	// The attributes are presented here for reference, and have no observable effects.
	"defaults" : {
		"version" : "termite-2.0.6",
										// Data
		"dataID" : undefined,				// @type {string}     Unique identifier for the current dataset
			"fullMatrix" : [],			// @type {number[][]} Matrix entries as a 2D array
			"rowDims" : 0,				// @type {number}     Number of rows in the matrix
			"columnDims" : 0,			// @type {number}     Number of columns in the matrix
			"rowAdmissions" : [],		// @type {boolean[]}
			"columnAdmissions" : []		// @type {boolean[]}
	}
});

MatrixState.prototype.initialize = function( options ) {
	this.__initUpdates();
};

//--------------------------------------------------------------------------------------------------

MatrixState.prototype.CONST = {
	ROW_PREFIX : "Row",
	COLUMN_PREFIX : "Column",
	MIN_VISIBLE_ROW_QUANTILE : 0,
	MAX_VISIBLE_ROW_QUANTILE : 80,
	MIN_VISIBLE_ROW_COUNT : 0,
	MAX_VISIBLE_ROW_COUNT : 200,
	MIN_ORDERED_ROW_QUANTILE : 0,
	MAX_ORDERED_ROW_QUANTILE : 60,
	MIN_ORDERED_ROW_COUNT : 0,
	MAX_ORDERED_ROW_COUNT : 150,
	SELECTION_COUNT : 8,
	SELECTION_PREFIX : "Selection",
	SELECTION_LABELS : [ "Blue topics", "Orange topics", "Green topics", "Purple topics", "Brown topics", "Pink topics", "Yellow topics", "Aqua topics" ],
	SELECTION_COLORS : [ "#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#8c564b", "#e377c2", "#bcbd22", "#17becf" ],
	SELECTION_BACKGROUNDS : [ "#aec7e8", "#ffbb78", "#98df8a", "#c5b0d5", "#c49c94", "#f7b6d2", "#dbdb8d", "#9edae5" ]
};

MatrixState.prototype.__resetParameters = function() {
	var rowDims = this.get( "rowDims" );
	var columnDims = this.get( "columnDims" );
	var selectionCount = this.CONST.SELECTION_COUNT;
	this.__reset({
											// Normalization
		"normalization" : "none",			// @type {string} How to normalize matrix entries; one of { "none", "row", "column" }

											// Visibility
		"rowInExclusions" : {},				// @type {{number:boolean}} Inclusions/exclusions of rows from the models
		"rowUserDefinedVisibilities" : {},	// @type {{number:boolean}} User-defined visible/hidden rows in the visualization
		"columnInExclusions" : {},
		"columnUserDefinedVisibilities" : {},
		
		"globalVisibleRowCount" : 25,		// @type {number} Number of rows to display, based on global column freqs
		"columnVisibleRowCounts" : {},		// @type {{number:number}} Column index and the number of rows to display, based on per-column freqs
		"selectionVisibleRowCounts" : {},	// @type {{number:number}} Selection index and the number of rows to display, based on per-column freqs
		"expansionVisibleRowCount" : 0,
		"globalVisibleRowQuantile" : 0,
		"columnVisibleRowQuantiles" : {},
		"selectionVisibleRowQuantiles" : {},
		"expansionVisibleRowQuantile" : 40,
											// User-specified ordering & Seriation (a.k.a. rule-based ordering)
		"rowOrderingType" : "auto", 		// @type {string} How to order matrix rows; one of { "auto", "user" }
		"rowCurrentOrdering" : null,
		"rowUserDefinedOrdering" : _.range( rowDims ),
		"columnOrderingType" : "user", 		// @type {string} How to order matrix rows; one of { "auto", "user" }
		"columnCurrentOrdering" : null,
		"columnUserDefinedOrdering" : _.range( columnDims ),

		"rowAutoOrderingBaseList" : _.range( rowDims ),
		"globalOrderedRowCount" : 0,
		"columnOrderedRowCounts" : {},
		"selectionOrderedRowCounts" : {},
		"expansionOrderedRowCount" : 0,
		"globalOrderedRowQuantile" : 0,
		"columnOrderedRowQuantiles" : {},
		"selectionOrderedRowQuantiles" : {},
		"expansionOrderedRowQuantile" : 0,
											// Highlights, expansions, selections, promotions/demotions
		"rowHighlights" : {},				// @type {{number:true}} Which row to highlight
		"columnHighlights" : {},			// @type {{number:true}} Which column to highlight
		"entryHighlights" : {},				// @type {{string:true}} Which entry to highlight (key = "rowIndex:colunmIndex")
		"rowExpansiosn" : {},				// @type {{number:true}} Which rows to expand
		"columnExpansions" : {},			// @type {{number:true}} Which columns to expand
		"rowSelections" : {},				// @type {{number:number}} Row index and its selection index
		"columnSelections" : {},			// @type {{number:number}} Column index and its selection index
		"entryProDemotions" : {},			// @type {{string:boolean}} A list of rows to associate/disassociate with a given column (key = "rowIndex:columnIndex")

											// Labels
		"rowLabels" : [],					// @type {string[]}  Descriptions for row elements
		"columnLabels" : [],				// @type {string[]}  Descriptions for column elements
		
		"selectionCount" : selectionCount,
		"selectionLabels" : this.CONST.SELECTION_LABELS.slice( 0, selectionCount ),
		"selectionColors" : this.CONST.SELECTION_COLORS.slice( 0, selectionCount ),
		"selectionBackgrounds" : this.CONST.SELECTION_BACKGROUNDS.slice( 0, selectionCount ),
		
		"rankingThreshold" : 0.0001,		// Exclude matrix cells whose values below this threshold during rendering.
		"highlightThreshold" : 0.0005	// Highlight matrix cells with values above this threshold during a highlight operation.
	});
};

//--------------------------------------------------------------------------------------------------

MatrixState.prototype.__initUpdates = function() {
	this.__triggerDirty = _.debounce( this.triggerDirty, 20 );
};

MatrixState.prototype.setAttributeAndDirty = function() {
	var keys = Array.prototype.slice.call( arguments, 0, arguments.length - 1 );
	CoreModel.prototype.setAttribute.apply( this, arguments );
	CoreModel.prototype.setDirty.apply( this, keys );
	this.__triggerDirty();
};

MatrixState.prototype.__reset = function( keysAndValues ) {
	for ( var key in keysAndValues ) {
		var value = keysAndValues[ key ];
		CoreModel.prototype.setAttribute.call( this, key, value );
		CoreModel.prototype.setDirty.call( this, key );
	}
	this.__triggerDirty();
};

//--------------------------------------------------------------------------------------------------
// Data

/**
 * Read in an array of matrix entries.
 * Infer row and column dimensions if not specified.
 * @param {Object[]} entries An array of matrix entries, where each entry consists of { rowIndex : number, columnIndex : number, value : number }
 * @param {number} [rowDims] Number of rows in the matrix.
 * @param {number} [columnDims] Number of columns in the matrix.
 * @param {boolean[]} [rowAdmissions] Whether a row is used in the construction of the matrix; default is no.
 * @param {boolean[]} [columnAdmissions] Whether a column is used in the construction of the matrix; default is yes.
 **/
MatrixState.prototype.importEntries = function( dataID, entries, rowDims, columnDims, rowAdmissions, columnAdmissions ) {
	if ( rowDims === undefined )
		rowDims = _.max( entries.map( function(d) { return d.rowIndex } ) ) + 1;
	if ( columnDims === undefined )
		columnDims = _.max( entries.map( function(d) { return d.columnIndex } ) ) + 1;
	if ( rowAdmissions === undefined )
		rowAdmissions = _.range( rowDims ).map( function(d) { return false } );
	if ( columnAdmissions === undefined )
		columnAdmissions = _.range( columnDims ).map( function(d) { return true } );

	var fullMatrix = this.__createFullMatrix( rowDims, columnDims );
	for ( var n = 0; n < entries.length; n++ ) {
		var entry = entries[n];
		var s = entry.rowIndex;
		var t = entry.columnIndex;
		if ( 0 <= s && s < rowDims  &&  0 <= t && t < columnDims ) {
			fullMatrix[s][t].absValue = entry.value;
		}
	}
	this.setAttributeAndDirtyFullMatrix( dataID, rowDims, columnDims, fullMatrix, rowAdmissions, columnAdmissions );
	return this;
};

/**
 * Read in a two-dimensional matrix of numbers.
 * Infer row and column dimensions if not specified.
 * @param {number[]} matrix A two dimensional array of values for the matrix.
 * @param {number} [rowDims] Number of rows in the matrix.
 * @param {number} [columnDims] Number of columns in the matrix.
 * @param {boolean[]} [rowAdmissions] Whether a row is used in the construction of the matrix; default is no.
 * @param {boolean[]} [columnAdmissions] Whether a column is used in the construction of the matrix; default is yes.
 **/
MatrixState.prototype.importMatrix = function( dataID, matrix, rowDims, columnDims, rowAdmissions, columnAdmissions ) {
	if ( rowDims === undefined )
		rowDims = matrix.length;
	if ( columnDims === undefined )
		columnDims = _.max( matrix.map( function(d) { return d.length } ) );
	if ( rowAdmissions === undefined )
		rowAdmissions = _.range( rowDims ).map( function(d) { return false } );
	if ( columnAdmissions === undefined )
		columnAdmissions = _.range( columnDims ).map( function(d) { return true } );
		
	var fullMatrix = this.__createFullMatrix( rowDims, columnDims );
	var sMax = Math.min( rowDims, matrix.length );
	for ( var s = 0; s < sMax; s++ ) {
		var tMax = Math.min( columnDims, matrix[s].length );
		for ( var t = 0; t < tMax; t++ ) {
			fullMatrix[s][t].absValue = matrix[s][t];
		}
	}
	this.setAttributeAndDirtyFullMatrix( dataID, rowDims, columnDims, fullMatrix, rowAdmissions, columnAdmissions );
	return this;
};

/** @private **/
MatrixState.prototype.__createFullMatrix = function( rowDims, columnDims ) {
	var fullMatrix = new Array( rowDims );
	for ( var s = 0; s < rowDims; s++ ) {
		var fullRow = new Array( columnDims );
		for ( var t = 0; t < columnDims; t++ )
			fullRow[t] = { "rowIndex" : s, "columnIndex" : t, "absValue" : 0.0 };
		fullMatrix[s] = fullRow;
	}
	return fullMatrix;
};

/** @private **/
MatrixState.prototype.setAttributeAndDirtyFullMatrix = function( dataID, rowDims, columnDims, fullMatrix, rowAdmissions, columnAdmissions ) {
	this.setDirty();
	this.__reset({
		"dataID" : dataID,
		"rowDims" : rowDims, 
		"columnDims" : columnDims, 
		"fullMatrix" : fullMatrix,
		"rowAdmissions" : rowAdmissions,
		"columnAdmissions" : columnAdmissions
	});
	this.__resetParameters();
};

//--------------------------------------------------------------------------------------------------
// Normalization

/**
 * Normalize all matrix entries by rows, columns, or neither.
 * Normalization produces a conditional probability distributions P(column|row) or P(row|column).
 * Otherwise, joint probability distributions P(row, column) are generated.
 * @param {string} normalization One of "row", "column", or "none".
 */
MatrixState.prototype.normalization = function( normalization ) {
	normalization = normalization.trim().toLowerCase();
	if ( normalization === "row" || normalization === "column" || normalization === "none" )
		if ( this.getAttribute( "normalization" ) !== normalization )
			this.setAttributeAndDirty( "normalization", normalization );
	return this;
};

//--------------------------------------------------------------------------------------------------
// Visibilities

MatrixState.prototype.rowInclusionsAndExclusions = function( index, isIncludedOrExcluded ) {
	if ( 0 <= index && index < this.get( "rowDims" ) )
		if ( isIncludedOrExcluded === true || isIncludedOrExcluded === false || isIncludedOrExcluded === undefined )
			if ( this.getAttribute( "rowInExclusions", index ) !== isIncludedOrExcluded )
				this.setAttributeAndDirty( "rowInExclusions", index, isIncludedOrExcluded );
	return this;
};

MatrixState.prototype.rowUserDefinedVisibilities = function( index, isVisibleOrHidden ) {
	if ( 0 <= index && index < this.get( "rowDims" ) )
		if ( isVisibleOrHidden === true || isVisibleOrHidden === false || isVisibleOrHidden === undefined )
			if ( this.getAttribute( "rowUserDefinedVisibilities", index ) !== isVisibleOrHidden )
				this.setAttributeAndDirty( "rowUserDefinedVisibilities", index, isVisibleOrHidden );
	return this;
};

MatrixState.prototype.globalVisibleRowCount = function( visibleRowCount ) {
	if ( this.CONST.MIN_VISIBLE_ROW_COUNT <= visibleRowCount && visibleRowCount <= this.CONST.MAX_VISIBLE_ROW_COUNT )
		if ( this.getAttribute( "globalVisibleRowCount" ) !== visibleRowCount )
			this.setAttributeAndDirty( "globalVisibleRowCount", visibleRowCount );
	return this;
};
MatrixState.prototype.columnVisibleRowCounts = function( index, visibleRowCount ) {
	if ( 0 <= index && index < this.get( "columnDims" ) )
		if ( 0 <= visibleRowCount )
			if ( this.getAttribute( "columnVisibleRowCounts", index ) !== visibleRowCount )
				this.setAttributeAndDirty( "columnVisibleRowCounts", index, visibleRowCount );
	return this;
};
MatrixState.prototype.selectionVisibleRowCounts = function( index, visibleRowCount ) {
	if ( 0 <= index && index < this.get( "selectionCount" ) )
		if ( 0 <= visibleRowCount )
			if ( this.getAttribute( "selectionVisibleRowCounts", index ) !== visibleRowCount )
				this.setAttributeAndDirty( "selectionVisibleRowCounts", index, visibleRowCount );
	return this;
};

MatrixState.prototype.globalVisibleRowQuantile = function( visibleRowQuantile ) {
	if ( 0 <= visibleRowQuantile && visibleRowQuantile <= 100 )
		if ( this.getAttribute( "globalVisibleRowQuantiles" ) !== visibleRowQuantile )
			this.setAttributeAndDirty( "globalVisibleRowQuantiles", visibleRowQuantile );
	return this;
};
MatrixState.prototype.columnVisibleRowQuantiles = function( index, visibleRowQuantile ) {
	if ( 0 <= index && index < this.get( "columnDims" ) )
		if ( 0 <= visibleRowQuantile )
			if ( this.getAttribute( "columnVisibleRowQuantiles", index ) !== visibleRowQuantile )
				this.setAttributeAndDirty( "columnVisibleRowQuantiles", index, visibleRowQuantile );
	return this;
};
MatrixState.prototype.selectionVisibleRowQuantiles = function( index, visibleRowQuantile ) {
	if ( 0 <= index && index < this.get( "selectionCount" ) )
		if ( 0 <= visibleRowQuantile )
			if ( this.getAttribute( "selectionVisibleRowQuantiles", index ) !== visibleRowQuantile )
				this.setAttributeAndDirty( "selectionVisibleRowQuantiles", index, visibleRowQuantile );
	return this;
};

//--------------------------------------------------------------------------------------------------
// Ordering

MatrixState.prototype.rowAutoOrdering = function( ordering ) {
	var rowOrderingType = "auto";
	if ( this.getAttribute( "rowOrderingType" ) !== rowOrderingType ) {
		this.setAttributeAndDirty( "rowOrderingType", rowOrderingType );
		if ( ordering === undefined )
			ordering = this.getAttribute( "rowCurrentOrdering" );
		
		var rowDims = this.get( "rowDims" );
		var rowAutoOrderingBaseList = this.__sanitizeOrdering( rowDims, ordering )
		this.setAttributeAndDirty( "rowAutoOrderingBaseList", rowAutoOrderingBaseList );
		this.setAttributeAndDirty( "globalOrderedRowCount", 0.0 );
		this.setAttributeAndDirty( "columnOrderedRowCounts", {} );
		this.setAttributeAndDirty( "selectionOrderedRowCounts", {} );
		this.setAttributeAndDirty( "globalOrderedRowQuantile", 0.0 );
		this.setAttributeAndDirty( "columnOrderedRowQuantiles", {} );
		this.setAttributeAndDirty( "selectionOrderedRowQuantiles", {} );
	}
	return this;
};

MatrixState.prototype.globalOrderedRowCount = function( orderedRowCount ) {
	this.rowAutoOrdering();
	if ( this.CONST.MIN_ORDERED_ROW_COUNT <= orderedRowCount && orderedRowCount <= this.CONST.MAX_ORDERED_ROW_COUNT )
		if ( this.getAttribute( "globalOrderedRowCount" ) !== orderedRowCount )
			this.setAttributeAndDirty( "globalOrderedRowCount", orderedRowCount );
	return this;
};
MatrixState.prototype.columnOrderedRowCounts = function( index, orderedRowCount ) {
	this.rowAutoOrdering();
	if ( 0 <= index && index < this.get( "columnDims" ) )
		if ( this.CONST.MIN_ORDERED_ROW_COUNT <= orderedRowCount && orderedRowCount <= this.CONST.MAX_ORDERED_ROW_COUNT )
			if ( this.getAttribute( "columnOrderedRowCounts", index ) !== orderedRowCount )
				this.setAttributeAndDirty( "columnOrderedRowCounts", index, orderedRowCount );
	return this;
};
MatrixState.prototype.selectionOrderedRowCounts = function( index, orderedRowCount ) {
	this.rowAutoOrdering();
	if ( 0 <= index && index < this.get( "selectionCount" ) )
		if ( this.CONST.MIN_ORDERED_ROW_COUNT <= orderedRowCount && orderedRowCount <= this.CONST.MAX_ORDERED_ROW_COUNT )
			if ( this.getAttribute( "selectionOrderedRowCounts", index ) !== orderedRowCount )
				this.setAttributeAndDirty( "selectionOrderedRowCounts", index, orderedRowCount );
	return this;
};

MatrixState.prototype.globalOrderedRowQuantile = function( orderedRowQuantile ) {
	this.rowAutoOrdering();
	if ( 0 <= orderedRowQuantile && orderedRowQuantile <= 100 )
		if ( this.getAttribute( "globalOrderedRowQuantiles" ) !== orderedRowQuantile )
			this.setAttributeAndDirty( "globalOrderedRowQuantiles", orderedRowQuantile );
	return this;
};
MatrixState.prototype.columnOrderedRowQuantiles = function( index, orderedRowQuantile ) {
	this.rowAutoOrdering();
	if ( 0 <= index && index < this.get( "columnDims" ) )
		if ( 0 <= orderedRowQuantile && orderedRowQuantile <= 100 )
			if ( this.getAttribute( "columnOrderedRowQuantiles", index ) !== orderedRowQuantile )
				this.setAttributeAndDirty( "columnOrderedRowQuantiles", index, orderedRowQuantile );
	return this;
};
MatrixState.prototype.selectionOrderedRowQuantiles = function( index, orderedRowQuantile ) {
	this.rowAutoOrdering();
	if ( 0 <= index && index < this.get( "selectionCount" ) )
		if ( 0 <= orderedRowQuantile && orderedRowQuantile <= 100 )
			if ( this.getAttribute( "selectionOrderedRowQuantiles", index ) !== orderedRowQuantile )
				this.setAttributeAndDirty( "selectionOrderedRowQuantiles", index, orderedRowQuantile );
	return this;
};

MatrixState.prototype.rowUserDefinedOrdering = function( ordering ) {
	var rowOrderingType = "user"
	if ( this.getAttribute( "rowOrderingType" ) !== rowOrderingType )
		this.setAttributeAndDirty( "rowOrderingType", rowOrderingType );

	var rowDims = this.get( "rowDims" );
	var rowUserDefinedOrdering = this.__sanitizeOrdering( rowDims, ordering )
	this.setAttributeAndDirty( "rowUserDefinedOrdering", rowUserDefinedOrdering );
	return this;
};

MatrixState.prototype.columnUserDefinedOrdering = function( ordering ) {
	var rowOrderingType = "user"
	if (  this.getAttribute( "columnOrderingType" ) !== rowOrderingType )
		this.setAttributeAndDirty( "columnOrderingType", rowOrderingType );

	var columnDims = this.get( "columnDims" );
	var columnUserDefinedOrdering = this.__sanitizeOrdering( columnDims, ordering )
	this.setAttributeAndDirty( "columnUserDefinedOrdering", columnUserDefinedOrdering );
	return this;
};

/**
 * Duplicate indexes are removed from the list.
 * Unpsecified indexes are appended at the end of the list.
**/
MatrixState.prototype.__sanitizeOrdering = function( N, list ) {
	var ordering = [];
	var existingIndexes = {};
	for ( var i = 0; i < list.length; i++ ) {
		var index = list[i];
		if ( 0 <= index && index < N )
			if ( ! existingIndexes.hasOwnProperty(index) ) {
				ordering.push( index );
				existingIndexes[ index ] = true;
			}
	}
	for ( var index = 0; index < N; index++ )
		if ( ! existingIndexes.hasOwnProperty(index) )
			ordering.push( index );
	return ordering;
};

/**
 * Move a row to after another row.
 * @param {number} rowIndex Row to reorder.
 * @param {number} previousRowIndex The row immediately before the reordered row.
 */
MatrixState.prototype.moveRowAfter = function( rowIndex, previousRowIndex ) {
	var rowDims = this.get( "rowDims" );
	if ( 0 <= rowIndex && rowIndex < rowDims )
		if ( 0 <= previousRowIndex && previousRowIndex < rowDims ) {
			var rowCurrentOrdering = this.get( "rowCurrentOrdering" );
			var rowUserDefinedOrdering = this.__getMoveAfterOrdering( rowDims, rowCurrentOrdering, rowIndex, previousRowIndex );
			this.rowUserDefinedOrdering( rowUserDefinedOrdering );
		}
	return this;
};

/**
 * Move a row to before another row.
 * @param {number} rowIndex Row to reorder.
 * @param {number} nextRowIndex The row immediately after the reordered row.
 */
MatrixState.prototype.moveRowBefore = function( rowIndex, nextRowIndex ) {
	var rowDims = this.get( "rowDims" );
	if ( 0 <= rowIndex && rowIndex < rowDims )
		if ( 0 <= nextRowIndex && nextRowIndex < rowDims ) {
			var rowCurrentOrdering = this.get( "rowCurrentOrdering" );
			var rowUserDefinedOrdering = this.__getMoveBeforeOrdering( rowDims, rowCurrentOrdering, rowIndex, nextRowIndex );
			this.rowUserDefinedOrdering( rowUserDefinedOrdering );
		}
	return this;
};

/**
 * Move a column to after another column.
 * @param {number} columnIndex Column to reorder.
 * @param {number} previousColumnIndex The column immediately before the reordered column.
 */
MatrixState.prototype.moveColumnAfter = function( columnIndex, previousColumnIndex ) {
	var columnDims = this.get( "columnDims" );
	if ( 0 <= columnIndex && columnIndex < columnDims )
		if ( 0 <= previousColumnIndex && previousColumnIndex < columnDims ) {
			var columnCurrentOrdering = this.get( "columnCurrentOrdering" );
			var columnUserDefinedOrdering = this.__getMoveAfterOrdering( columnDims, columnCurrentOrdering, columnIndex, previousColumnIndex );
			this.columnUserDefinedOrdering( columnUserDefinedOrdering );
		}
	return this;
};

/**
 * Move a column to before another column.
 * @param {number} columnIndex Column to reorder.
 * @param {number} nextColumnIndex The column immediately after the reordered column.
 */
MatrixState.prototype.moveColumnBefore = function( columnIndex, nextColumnIndex ) {
	var columnDims = this.get( "columnDims" );
	if ( 0 <= columnIndex && columnIndex < columnDims )
		if ( 0 <= nextColumnIndex && nextColumnIndex < columnDims ) {
			var columnCurrentOrdering = this.get( "columnCurrentOrdering" );
			var columnUserDefinedOrdering = this.__getMoveBeforeOrdering( columnDims, columnCurrentOrdering, columnIndex, nextColumnIndex );
			this.columnUserDefinedOrdering( columnUserDefinedOrdering );
		}
	return this;
};

MatrixState.prototype.__getMoveAfterOrdering = function( N, ordering, index, previousIndex ) {
	var a = ordering.indexOf( index );
	var tempOrdering = ordering.slice( 0, a ).concat( ordering.slice( a+1 ) );
	var b = tempOrdering.indexOf( previousIndex );
	tempOrdering.splice( b+1, 0, index );
	return tempOrdering;
};

MatrixState.prototype.__getMoveBeforeOrdering = function( N, ordering, index, nextIndex ) {
	var a = ordering.indexOf( index );
	var tempOrdering = ordering.slice( 0, a ).concat( ordering.slice( a+1 ) );
	var b = tempOrdering.indexOf( nextIndex );
	tempOrdering.splice( b, 0, index );
	return tempOrdering;
};

//--------------------------------------------------------------------------------------------------
// Highlights, Selections, Expansions

MatrixState.prototype.rowHighlights = function( index ) {
	if ( 0 <= index && index < this.get( "rowDims" ) )
		if ( this.getAttribute( "rowHighlights", index ) !== true ) {
			for ( var s in this.get( "rowHighlights" ) ) { this.setAttributeAndDirty( "rowHighlights", s, undefined ) }
			for ( var t in this.get( "columnHighlights" ) ) { this.setAttributeAndDirty( "columnHighlights", t, undefined ) }
			for ( var key in this.get( "entryHighlights" ) ) { this.setAttributeAndDirty( "entryHighlights", key, undefined ) }
			this.setAttributeAndDirty( "rowHighlights", index, true );
		}
	return this;
};

MatrixState.prototype.columnHighlights = function( index ) {
	if ( 0 <= index && index < this.get( "columnDims" ) )
		if ( this.getAttribute( "columnHighlights", index ) !== true ) {
			for ( var s in this.get( "rowHighlights" ) ) { this.setAttributeAndDirty( "rowHighlights", s, undefined ) }
			for ( var t in this.get( "columnHighlights" ) ) { this.setAttributeAndDirty( "columnHighlights", t, undefined ) }
			for ( var key in this.get( "entryHighlights" ) ) { this.setAttributeAndDirty( "entryHighlights", key, undefined ) }
			this.setAttributeAndDirty( "columnHighlights", index, true );
		}
	return this;
};

MatrixState.prototype.entryHighlights = function( rowIndex, columnIndex ) {
	var entryKey = rowIndex + ":" + columnIndex;
	if ( 0 <= rowIndex && rowIndex < this.get( "rowDims" ) )
		if ( 0 <= columnIndex && columnIndex < this.get( "columnDims" ) )
			if ( this.getAttribute( "entryHighlights", entryKey ) !== true ) {
				for ( var s in this.get( "rowHighlights" ) ) { this.setAttributeAndDirty( "rowHighlights", s, undefined ) }
				for ( var t in this.get( "columnHighlights" ) ) { this.setAttributeAndDirty( "columnHighlights", t, undefined ) }
				for ( var key in this.get( "entryHighlights" ) ) { this.setAttributeAndDirty( "entryHighlights", key, undefined ) }
				this.setAttributeAndDirty( "entryHighlights", entryKey, true );
			}
	return this;
};

MatrixState.prototype.noHighlights = function() {
	for ( var s in this.getAttribute( "rowHighlights" ) ) { this.setAttributeAndDirty( "rowHighlights", s, undefined ) }
	for ( var t in this.getAttribute( "columnHighlights" ) ) { this.setAttributeAndDirty( "columnHighlights", t, undefined ) }
	for ( var key in this.getAttribute( "entryHighlights" ) ) { this.setAttributeAndDirty( "entryHighlights", key, undefined ) }
	return this;
};

MatrixState.prototype.rowExpansions = function( index ) {
	if ( 0 <= index && index < this.get( "rowDims" ) )
		if ( this.getAttribute( "rowExpansions", index ) !== true ) {
			for ( var s in this.getAttribute( "rowExpansions" ) ) { this.setAttributeAndDirty( "rowExpansions", s, undefined ) }
			for ( var t in this.getAttribute( "columnExpansions" ) ) { this.setAttributeAndDirty( "columnExpansions", t, undefined ) }
			this.setAttributeAndDirty( "rowExpansions", index, true );
		}
	return this;
};

MatrixState.prototype.columnExpansions = function( index ) {
	if ( 0 <= index && index < this.get( "columnDims" ) )
		if ( this.getAttribute( "columnExpansions", index ) !== true ) {
			for ( var s in this.getAttribute( "rowExpansions" ) ) { this.setAttributeAndDirty( "rowExpansions", s, undefined ) }
			for ( var t in this.getAttribute( "columnExpansions" ) ) { this.setAttributeAndDirty( "columnExpansions", t, undefined ) }
			this.setAttributeAndDirty( "columnExpansions", index, true );
		}
	return this;
};

MatrixState.prototype.noExpansions = function() {
	for ( var s in this.getAttribute( "rowExpansions" ) ) { this.setAttributeAndDirty( "rowExpansions", s, undefined ) }
	for ( var t in this.getAttribute( "columnExpansions" ) ) { this.setAttributeAndDirty( "columnExpansions", t, undefined ) }
	return this;
};

MatrixState.prototype.expandNextColumn = function() {
	var thisColumnExpansion = _.keys( this.state.get( "columnExpansions" ) ).map( function(d) { return parseInt(d) } )[0];
	if ( thisColumnExpansion !== undefined ) {
		var columnDims = this.get( "columnDims" );
		var columnOrderingType = this.get( "columnOrderingType" );
		var index = columnOrderingType.indexOf( thisColumnExpansion );
		nextColumnExpansion = columnOrderingType[ ( index + 1 ) % columnDims ];
		this.columnExpansions( nextColumnExpansion );
	}
	return this;
};

MatrixState.prototype.expandPreviousColumn = function() {
	var thisColumnExpansion = _.keys( this.state.get( "columnExpansions" ) ).map( function(d) { return parseInt(d) } )[0];
	if ( thisColumnExpansion !== undefined ) {
		var columnDims = this.get( "columnDims" );
		var columnOrderingType = this.get( "columnOrderingType" );
		var index = columnOrderingType.indexOf( columnExpansions );
		prevColumnExpansion = columnOrderingType[ ( index + columnDims - 1 ) % columnDims ];
		this.columnExpansions( prevColumnExpansion );
	}
	return this;
};

MatrixState.prototype.rowSelections = function( index, selection ) {
	if ( 0 <= index && index < this.get( "rowDims" ) )
		if ( 0 <= selection && selection < this.get( "selectionCount" ) || selection === undefined )
			if ( this.getAttribute( "rowSelections", index ) !== selection )
				this.setAttributeAndDirty( "rowSelections", index, selection );
	return this;
};

MatrixState.prototype.columnSelections = function( index, selection ) {
	if ( 0 <= index && index < this.get( "columnDims" ) )
		if ( 0 <= selection && selection < this.get( "selectionCount" ) || selection === undefined )
			if ( this.getAttribute( "columnSelections", index ) !== selection )
				this.setAttributeAndDirty( "columnSelections", index, selection );
	return this;
};

MatrixState.prototype.noSelections = function() {
	for ( var s in this.getAttribute( "rowSelections" ) ) { this.setAttributeAndDirty( "rowSelections", s, undefined ) }
	for ( var t in this.getAttribute( "columnSelections" ) ) { this.setAttributeAndDirty( "columnSelections", t, undefined ) }
	return this;
};

//--------------------------------------------------------------------------------------------------
// Promotions & demotions

MatrixState.prototype.entryPromotionsAndDemotions = function( rowIndex, columnIndex, isPromotedOrDemoted ) {
	if ( 0 <= rowIndex && rowIndex < this.get( "rowDims" ) )
		if ( 0 <= columnIndex && columnIndex < this.get( "columnDims" ) ) {
			var key = rowIndex + ":" + columnIndex;
			if ( isPromotedOrDemoted === true || isPromotedOrDemoted === false || isPromotedOrDemoted === undefined )
				if ( this.getAttribute( "entryProDemotions", key ) !== isPromotedOrDemoted )
					this.setAttributeAndDirty( "entryProDemotions", key, isPromotedOrDemoted );
		}
	return this;
};

//--------------------------------------------------------------------------------------------------
// Labels

MatrixState.prototype.rowLabels = function( index, label ) {
	if ( 0 <= index && index < this.get( "rowDims" ) )
		if ( this.getAttribute( "rowLabels", index ) !== label )
			this.setAttributeAndDirty( "rowLabels", index, label );
	return this;
};

MatrixState.prototype.columnLabels = function( index, label ) {
	if ( 0 <= index && index < this.get( "columnDims" ) )
		if ( this.getAttribute( "columnLabels", index ) !== label )
			this.setAttributeAndDirty( "columnLabels", index, label );
	return this;
};

MatrixState.prototype.allRowLabels = function( labels ) {
	var rowDims = this.get( "rowDims" );
	var rowLabels = this.__initLabels( rowDims, this.CONST.ROW_PREFIX );
	for ( var s = 0; s < rowLabels.length && s < labels.length; s++ )
		rowLabels[s] = labels[s];
	this.setAttributeAndDirty( "rowLabels", rowLabels );
	return this;
};

MatrixState.prototype.allColumnLabels = function( labels ) {
	var columnDims = this.get( "columnDims" );
	var columnLabels = this.__initLabels( columnDims, this.CONST.COLUMN_PREFIX );
	for ( var s = 0; s < columnLabels.length && s < labels.length; s++ )
		columnLabels[s] = labels[s];
	this.setAttributeAndDirty( "columnLabels", columnLabels );
	return this;
};

MatrixState.prototype.__initLabels = function( N, prefix ) {
	var labels = new Array( N );
	for ( var i = 0; i < N; i++ )
		labels[ i ] = prefix + " #" + (i+1);
	return labels;
}

//--------------------------------------------------------------------------------------------------

MatrixState.prototype.selectionLabels = function( index, label ) {
	if ( 0 <= index && index < this.get( "selectionCount" ) )
		if ( this.getAttribute( "selectionLabels", index ) !== label )
			this.setAttributeAndDirty( "selectionLabels", index, label );
	return this;
};

MatrixState.prototype.selectionColors = function( index, color ) {
	if ( 0 <= index && index < this.get( "selectionCount" ) )
		if ( this.getAttribute( "selectionColors", index ) !== color )
			this.setAttributeAndDirty( "selectionColors", index, color );
	return this;
};

MatrixState.prototype.selectionBackgrounds = function( index, background ) {
	if ( 0 <= index && index < this.get( "selectionCount" ) )
		if ( this.getAttribute( "selectionBackgrounds", index ) !== background )
			this.setAttributeAndDirty( "selectionBackgrounds", index, background );
	return this;
};

//--------------------------------------------------------------------------------------------------
// Compatibility with Node.js

if ( typeof module !== "undefined" ) {
	module.exports = MatrixState;
}
