MatrixModel.prototype.__initEntries = function() {
	if ( this.__isDirtyState( "dataID" ) ) {
		var sparseMatrix = this.state.__data__.sparseMatrix;
		var rowDims = this.state.__data__.rowDims;
		var columnDims = this.state.__data__.columnDims;
		var rowAdmissions = this.state.__data__.rowAdmissions;
		var columnAdmissions = this.state.__data__.columnAdmissions;
		
		var allEntries = initAllEntries( rowDims, columnDims, sparseMatrix );
		var allRowElements = initAllRowElements( rowDims, rowAdmissions );
		var allColumnElements = initAllColumnElements( columnDims, columnAdmissions );
		var allRowCrossRefs = initAllRowCrossRefs( rowDims, columnDims );
		var allColumnCrossRefs = initAllColumnCrossRefs( rowDims, columnDims );
		
		var allRowMetas = initAllRowMetas( allRowElements );
		var allColumnMetas = initAllColumnMetas( allColumnElements );
		var hashEntries = initHashEntries( allEntries );
		var hashRowCrossRefs = initHashRowCrossRefs( allRowCrossRefs );
		var hashColumnCrossRefs = initHashColumnCrossRefs( allColumnCrossRefs );
		this.setDirty();
		this.__setDirtyModelAndValues({
			"allEntries" : allEntries,
			"allRowElements" : allRowElements,
			"allColumnElements" : allColumnElements,
			"allRowCrossRefs" : allRowCrossRefs,
			"allColumnCrossRefs" : allColumnCrossRefs,
			"allRowMetas" : allRowMetas,
			"allColumnMetas" : allColumnMetas,
			"hashEntries" : hashEntries,
			"hashRowCrossRefs" : hashRowCrossRefs,
			"hashColumnCrossRefs" : hashColumnCrossRefs
		});
	}
	
	// All entries should have properties: rowIndex, columnIndex, absValue, hasEntry, dataType
	function initAllEntries( rowDims, columnDims, sparseMatrix ) {
		var allEntries = [];
		for ( var i = 0; i < sparseMatrix.length; i++ ) {
			var entry = sparseMatrix[i];
			entry.key = entry["rowIndex"] + ":" + entry["columnIndex"];
			entry.dataType = "cell";
			entry.absValue = entry.value;
			entry.hasEntry = true;
			allEntries.push( entry );
		}
		allEntries.sort( function(a,b) { return b.absValue - a.absValue } );
		return allEntries;
	}
	function initHashEntries( allEntries ) {
		var hashEntries = {};
		for ( var n = 0; n < allEntries.length; n++ ) {
			var entry = allEntries[n];
			hashEntries[ entry.key ] = entry;
		}
		return hashEntries;
	}
	// All row elements should have properties: index, rowIndex, absValue, dataType, crossRefs, isAdmitted
	function initAllRowElements( rowDims, rowAdmissions ) {
		var allRowElements = new Array( rowDims );
		for ( var s = 0; s < rowDims; s++ ) {
			var element = {
				"key" : s,
				"rowIndex" : s,
				"absValue" : 0.0,
				"dataType" : "row",
				"crossRefs" : {},
				"isAdmitted" : rowAdmissions[s]
			};
			allRowElements[s] = element;
		}
		for ( var n = 0; n < allEntries.length; n++ ) {
			var entry = allEntries[n];
			allRowElements[ entry.rowIndex ].absValue += entry.absValue;
		}
		return allRowElements;
	}
	// All column elements should have properties: index, columnIndex, absValue, dataType, crossRefs, isAdmitted
	function initAllColumnElements( columnDims, columnAdmissions ) {
		var allColumnElements = new Array( columnDims );
		for ( var t = 0; t < columnDims; t++ ) {
			var element = {
				"key" : t,
				"columnIndex" : t,
				"absValue" : 0.0,
				"dataType" : "column",
				"crossRefs" : {},
				"isAdmitted" : columnAdmissions[t]
			};
			allColumnElements[t] = element;
		}
		for ( var n = 0; n < allEntries.length; n++ ){
			var entry = allEntries[n];
			allColumnElements[ entry.columnIndex ].absValue += entry.absValue;
		}
		return allColumnElements;
	}
	// All row cross references should have properties: index, rowIndex, columnIndex, dataType, parent, entry
	function initAllRowCrossRefs( rowDims, columnDims ) {
		var allRowCrossRefs = [];
		for ( var n = 0; n < allEntries.length; n++ ){
			var entry = allEntries[n];
			var s = entry.rowIndex;
			var t = entry.columnIndex;
			var element = allRowElements[s];
			var crossRef = { 
				"key" : s + ":" + t,
				"rowIndex" : s, 
				"columnIndex" : t, 
				"dataType" : "column", 
				"parent" : element, 
				"entry" : entry
			};
			element.crossRefs[ t ] = crossRef;
			allRowCrossRefs.push( crossRef );
		}
				
		return allRowCrossRefs;
	}
	function initHashRowCrossRefs( allRowCrossRefs ) {
		var hashRowCrossRefs = {};
		for ( var st = 0; st < allRowCrossRefs.length; st++ ) {
			var crossRef = allRowCrossRefs[ st ];
			hashRowCrossRefs[ crossRef.key ] = crossRef;
		}
		return hashRowCrossRefs;
	}
	// All column cross references should have properties: index, columnIndex, rowIndex, dataType, parent, entry
	function initAllColumnCrossRefs( rowDims, columnDims ) {
		var allColumnCrossRefs = [];
		for ( var n = 0; n < allEntries.length; n++ ){
			var entry = allEntries[n];
			var s = entry.rowIndex;
			var t = entry.columnIndex;
			var element = allColumnElements[t];
			var crossRef = { 
				"key" : s + ":" + t,
				"rowIndex" : s, 
				"columnIndex" : t, 
				"dataType" : "row", 
				"parent" : element, 
				"entry" : entry
			};
			element.crossRefs[ s ] = crossRef;
			allColumnCrossRefs.push( crossRef );
		}
				
		return allColumnCrossRefs;
	}
	function initHashColumnCrossRefs( allColumnCrossRefs ) {
		var hashColumnCrossRefs = {};
		for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
			var crossRef = allColumnCrossRefs[ ts ];
			hashColumnCrossRefs[ crossRef.key ] = crossRef;
		}
		return hashColumnCrossRefs;
	}
	function initAllRowMetas( allRowElements ) {
		var allRowMetas = new Array( allRowElements.length );
		for ( var s = 0; s < allRowElements.length; s++ ) {
			var element = allRowElements[ s ];
			var meta = {
				"key" : s,
				"rowIndex" : s,
				"element" : element,
				"dataType" : "rowMeta"
			};
			allRowMetas[ s ] = meta;
		}
		return allRowMetas;
	}
	function initAllColumnMetas( allColumnElements ) {
		var allColumnMetas = new Array( allColumnElements.length );
		for ( var t = 0; t < allColumnElements.length; t++ ) {
			var element = allColumnElements[ t ];
			var meta = {
				"key" : t,
				"columnIndex" : t,
				"element" : element,
				"dataType" : "columnMeta",
				"visibility" : [{
					"key" : t,
					"columnIndex" : t,
					"element" : element,
					"dataType" : "columnVisibility"
				}],
				"ordering" : [{
					"key" : t,
					"columnIndex" : t,
					"element" : element,
					"dataType" : "columnOrdering"
				}]
			};
			allColumnMetas[ t ] = meta;
		}
		return allColumnMetas;
	}
};

/**
 * Pre-compute cell values for the three types of normalizations: relValue, rowRelValue, columnRelValue
 * Record maximum values under the three noramlization schemes: maxJointProbability, maxRowMarginalProbability, maxColumnMarginalProbability
 * Calculate scaling factor between joint and marginal probabilities: rowRescaleMultiplier, columnRescaleMultiplier
 * @private
 **/
MatrixModel.prototype.__precomputeRelValues = function() {
	if ( this.__isDirtyModel( [ "allEntries", "allRowElements", "allColumnElements" ], "absValue" ) )
	{
		var allEntries = this.get( "allEntries" );
		var allRowElements = this.get( "allRowElements" );
		var allColumnElements = this.get( "allColumnElements" );
		var maxJointProbability = 0.0;			// @type {number} Largest value in the joint probability distribution P(rows,columns)
		var maxRowMarginalProbability = 0.0;	// @type {number} Largest value in the marginal probability distribution P(rows)
		var maxColumnMarginalProbability = 0.0;	// @type {number} Largest value in the marginal probability distribution P(columns)
		var rowRescaleMultiplier = 0.0;			// @type {number} Row statistics: Rescaling factor to maintain the same number of painted pixels on the screen between P(rows,columns) -> P(rows)
		var columnRescaleMultiplier = 0.0;		// @type {number} Column statistics: Rescaling factor to maintain the same number of painted pixels on the screen between P(rows,columns) -> P(columns)

		// All entries should have additional properties: relValue, rowRelValue, columnRelValue
		// All row elements should have an additional property: relValue
		// All column elements should have an additional property: relValue
		precomputeEntryRelValues();
		precomputeRowElementRelValues();
		precomputeColumnElementRelValues();
		precomputeEntryRowRelValues();
		precomputeEntryColumnRelValues();

		this.__setDirtyModel( "allEntries", [ "relValue", "rowRelValue", "columnRelValue" ] );
		this.__setDirtyModel( "allRowElements", "relValue" );
		this.__setDirtyModel( "allColumnElements", "relValue" );
		this.__setDirtyModelAndValue( "maxJointProbability", maxJointProbability );
		this.__setDirtyModelAndValue( "maxRowMarginalProbability", maxRowMarginalProbability );
		this.__setDirtyModelAndValue( "maxColumnMarginalProbability", maxColumnMarginalProbability );
		this.__setDirtyModelAndValue( "rowRescaleMultiplier", rowRescaleMultiplier );
		this.__setDirtyModelAndValue( "columnRescaleMultiplier", columnRescaleMultiplier );
	}
	
	function precomputeEntryRelValues() {
		var totalAbsValue = 0.0;
		var maxAbsValue = 0.0;
		for ( var n = 0; n < allEntries.length; n++ ) {
			var absValue = allEntries[n].absValue;
			totalAbsValue += absValue;
			maxAbsValue = Math.max( maxAbsValue, absValue );
		}
		for ( var n = 0; n < allEntries.length; n++ ) {
			var entry = allEntries[n];
			entry.relValue = entry.absValue / totalAbsValue;
		}
		maxJointProbability = maxAbsValue / totalAbsValue;
	}
	function precomputeRowElementRelValues() {
		var totalAbsValue = 0.0;
		var maxAbsValue = 0.0;
		for ( var s = 0; s < allRowElements.length; s++ ) {
			var absValue = allRowElements[s].absValue;
			totalAbsValue += absValue;
			maxAbsValue = Math.max( maxAbsValue, absValue );
		}
		for ( var s = 0; s < allRowElements.length; s++ ) {
			var element = allRowElements[s];
			element.relValue = element.absValue / totalAbsValue;
		}
		maxRowMarginalProbability = maxAbsValue / totalAbsValue;
	}
	function precomputeColumnElementRelValues() {
		var totalAbsValue = 0.0;
		var maxAbsValue = 0.0;
		for ( var t = 0; t < allColumnElements.length; t++ ) {
			var absValue = allColumnElements[t].absValue;
			totalAbsValue += absValue;
			maxAbsValue = Math.max( maxAbsValue, absValue );
		}
		for ( var t = 0; t < allColumnElements.length; t++ ) {
			var element = allColumnElements[t];
			element.relValue = element.absValue / totalAbsValue;
		}
		maxColumnMarginalProbability = maxAbsValue / totalAbsValue;
	}
	function precomputeEntryRowRelValues() {
		var totalValue = 0.0;
		for ( var n = 0; n < allEntries.length; n++ ) {
			var entry = allEntries[n];
			var s = entry.rowIndex;
			var element = allRowElements[s];
			var value = entry.absValue / element.absValue;
			entry.rowRelValue = value;
			totalValue += value;
		}
		rowRescaleMultiplier = totalValue;
	}
	function precomputeEntryColumnRelValues() {
		var totalValue = 0.0;
		for ( var n = 0; n < allEntries.length; n++ ) {
			var entry = allEntries[n];
			var t = entry.columnIndex;
			var element = allColumnElements[t];
			var value = entry.absValue / element.absValue;
			entry.columnRelValue = value;
			totalValue += value;
		}
		columnRescaleMultiplier = totalValue;
	}
};

MatrixModel.prototype.__precomputeHighlights = function() {
	if ( this.__isDirtyState( "highlightThreshold" ) || this.__isDirtyModel( "allEntries", "relValue" ) ) {
		var highlightThreshold = this.state.get( "highlightThreshold" );
		var allEntries = this.get( "allEntries" );
		var allRowElements = this.get( "allRowElements" );
		var allColumnElements = this.get( "allColumnElements" );
		for ( var s = 0; s < allRowElements.length; s++ ) {
			var element = allRowElements[s];
			element.columnHighlights = {};
		}
		for ( var t = 0; t < allColumnElements.length; t++ ) {
			var element = allColumnElements[t];
			element.rowHighlights = {};
		}
		for ( var n = 0; n < allEntries.length; n++ ) {
			var entry = allEntries[n];
			var s = entry.rowIndex;
			var t = entry.columnIndex;
			if ( entry.relValue >= highlightThreshold ) {
				allRowElements[ s ].columnHighlights[ t ] = true;
				allColumnElements[ t ].rowHighlights[ s ] = true;
			}
		}
		this.__setDirtyModel( "allRowElements", "columnHighlights" );
		this.__setDirtyModel( "allColumnElements", "rowHighlights" );
	}	
}

MatrixModel.prototype.__precomputeRankingsAndQuantiles = function() {
	if ( this.__getDirtyState() === true )
	{
		var rankingThreshold = this.state.get( "rankingThreshold" );
		var allEntries = this.get( "allEntries" );
		var allRowElements = this.get( "allRowElements" );
		var allColumnElements = this.get( "allColumnElements" );
		var globalRowRankingIndexes = undefined;
		var globalRowRankingWeights = undefined;
		var globalRowQuantileIndexes = undefined;
		var globalRowQuantileCounts = undefined;
		var globalColumnRankingIndexes = undefined;
		var globalColumnRankingWeights = undefined;
		var globalColumnQuantileIndexes = undefined;
		var globalColumnQuantileCounts = undefined;

		// Compute global ranking of rows and columns
		precomputeGlobalRowRankingsAndQuantiles();
		precomputeGlobalColumnRankingsAndQuantiles();

		// Compute per-row and per-column ranking of columns and rows
		precomputeColumnRankingsAndQuantilesPerRow();
		precomputeRowRankingsAndQuantilesPerColumn();
		
		this.__setDirtyModelAndValue( "globalRowRankingIndexes", globalRowRankingIndexes );
		this.__setDirtyModelAndValue( "globalRowRankingWeights", globalRowRankingWeights );
		this.__setDirtyModelAndValue( "globalRowQuantileIndexes", globalRowQuantileIndexes );
		this.__setDirtyModelAndValue( "globalRowQuantileCounts", globalRowQuantileCounts );
		this.__setDirtyModelAndValue( "globalColumnRankingIndexes", globalColumnRankingIndexes );
		this.__setDirtyModelAndValue( "globalColumnRankingWeights", globalColumnRankingWeights );
		this.__setDirtyModelAndValue( "globalColumnQuantileIndexes", globalColumnQuantileIndexes );
		this.__setDirtyModelAndValue( "globalColumnQuantileCounts", globalColumnQuantileCounts );
		this.__setDirtyModel( "allRowElements", [ "columnRankingIndexes", "columnRankingWeights", "columnQuantileIndexes", "columnQuantileCounts" ] );
		this.__setDirtyModel( "allColumnElements", [ "rowRankingIndexes", "rowRankingWeights", "rowQuantileIndexes", "rowQuantileCounts" ] );
	}
	
	function precomputeGlobalRowRankingsAndQuantiles() {
		var rowList = [];
		for ( var s = 0; s < allRowElements.length; s++ ) {
			var element = allRowElements[s];
			if ( element.relValue >= rankingThreshold ) {
				rowList.push( { "index" : element.rowIndex, "relValue" : element.relValue } );
			}
		}
		var results = getRankingsAndQuantiles( rowList );
		globalRowRankingIndexes = results.rankingIndexes;
		globalRowRankingWeights = results.rankingWeights;
		globalRowQuantileIndexes = results.quantileIndexes;
		globalRowQuantileCounts = results.quantileCounts;
	}
	function precomputeGlobalColumnRankingsAndQuantiles() {
		var columnList = [];
		for ( var t = 0; t < allColumnElements.length; t++ ) {
			var element = allColumnElements[t];
			if ( element.relValue >= rankingThreshold ) {
				columnList.push( { "index" : element.columnIndex, "relValue" : element.relValue } );
			}
		}
		var results = getRankingsAndQuantiles( columnList );
		globalColumnRankingIndexes = results.rankingIndexes;
		globalColumnRankingWeights = results.rankingWeights;
		globalColumnQuantileIndexes = results.quantileIndexes;
		globalColumnQuantileCounts = results.quantileCounts;
	}
	function precomputeColumnRankingsAndQuantilesPerRow() {
		var rowLists = _.range( allRowElements.length ).map( function() { return [] } );
		for ( var n = 0; n < allEntries.length; n++ ) {
			var entry = allEntries[n];
			if ( entry.rowRelValue >= rankingThreshold ) {
				rowLists[ entry.rowIndex ].push( { "index" : entry.columnIndex, "relValue" : entry.rowRelValue } );
			}
		}
		for ( var s = 0; s < allRowElements.length; s++ ) {
			var results = getRankingsAndQuantiles( rowLists[s] );
			var element = allRowElements[s];
			element.columnRankingIndexes = results.rankingIndexes;
			element.columnRankingWeights = results.rankingWeights;
			element.columnQuantileIndexes = results.quantileIndexes;
			element.columnQuantileCounts = results.quantileCounts;
		}
	}
	function precomputeRowRankingsAndQuantilesPerColumn() {
		var columnLists = _.range( allColumnElements.length ).map( function() { return [] } );
		for ( var n = 0; n < allEntries.length; n++ ) {
			var entry = allEntries[n];
			if ( entry.columnRelValue >= rankingThreshold ) {
				columnLists[ entry.columnIndex ].push( { "index" : entry.rowIndex, "relValue" : entry.columnRelValue } );
			}
		}
		for ( var t = 0; t < allColumnElements.length; t++ ) {
			var results = getRankingsAndQuantiles( columnLists[t] );
			var element = allColumnElements[t];
			element.rowRankingIndexes = results.rankingIndexes;
			element.rowRankingWeights = results.rankingWeights;
			element.rowQuantileIndexes = results.quantileIndexes;
			element.rowQuantileCounts = results.quantileCounts;
		}
	}
	function getRankingsAndQuantiles( list ) {
		list.sort( function(a,b) { return b.relValue - a.relValue } );
		var weight = 1.0;
		for ( var i = 0; i < list.length; i++ ) {
			list[i].weight = weight;
			weight -= list[i].relValue;
		}
		var rankingIndexes = [];                      // ranking (absolute position) --> index
		var rankingWeights = [];						// ranking (absolute position) --> weights
		for ( var i = 0; i < list.length; i++ ) {
			rankingIndexes.push( list[i].index );
			rankingWeights.push( list[i].relValue );
		}
		var quantileIndexes = _.range( 100 ).map( function() { return [] } );  // percentile (relative position) --> indexes
		var quantileCounts = _.range( 100 ).map( function() { return 0 } );  // percentile (relative position) --> weights
		for ( var i = 0; i < list.length; i++ ) {
			var quantile = Math.max( 0, Math.min( 100, Math.floor( 100.0 - list[i].weight * 100.0 ) ) );
			quantileIndexes[ quantile ].push( list[i].index );
			quantileCounts[ quantile ] = i;
		}
		return {
			"rankingIndexes" : rankingIndexes,
			"rankingWeights" : rankingWeights,
			"quantileIndexes" : quantileIndexes, 
			"quantileCounts" : quantileCounts 
		};
	}
};
