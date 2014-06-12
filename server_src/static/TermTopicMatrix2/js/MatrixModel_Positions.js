MatrixModel.prototype.__updateRowAbsOrdering = function() {
	if ( this.__isDirtyState( "rowOrderingType" ) ||
		 this.__isDirtyState( "rowUserDefinedOrdering" ) ||
		 this.__isDirtyState( [ "rowAutoOrderingBaseList", 
			"globalOrderedRowCount", "globalOrderedRowQuantile",
			"columnOrderedRowCounts", "columnOrderedRowQuantiles",
			"selectionOrderedRowCounts", "selectionOrderedRowQuantiles",
			"expansionOrderedRowCounts", "expansionOrderedRowQuantiles" ] ) ||
		this.__isDirtyState( "columnExpansions" ) )
	{
		var rowOrderingType = this.state.get( "rowOrderingType" );
		var rowAbsOrdering = undefined;
		if ( rowOrderingType === "auto" )
			rowAbsOrdering = this.__getRowAutoOrdering();
		if ( rowOrderingType === "user" )
			rowAbsOrdering = this.state.get( "rowUserDefinedOrdering" );
		this.state.set( "rowCurrentOrdering", rowAbsOrdering );
		this.__setDirtyModelAndValue( "rowAbsOrdering", rowAbsOrdering );
	}
};

MatrixModel.prototype.__updateColumnAbsOrdering = function() {
	if ( this.__isDirtyState( "columnOrderingType" ) ||
		 this.__isDirtyState( "columnUserDefinedOrdering" ) )
	{
		var columnOrderingType = this.state.get( "columnOrderingType" );
		var columnAbsOrdering = undefined;
		if ( columnOrderingType === "auto" )
			columnAbsOrdering = this.__getColumnAutoOrdering();
		if ( columnOrderingType === "user" )
			columnAbsOrdering = this.state.get( "columnUserDefinedOrdering" );
		this.state.set( "columnCurrentOrdering", columnAbsOrdering );
		this.__setDirtyModelAndValue( "columnAbsOrdering", columnAbsOrdering );
	}
};

MatrixModel.prototype.__getRowAutoOrdering = function() {
	var addGlobalOrderedRows = function() {
		var globalRowRankingIndexes = this.get( "globalRowRankingIndexes" );
		var globalRowRankingWeights = this.get( "globalRowRankingWeights" );
		var globalRowQuantileIndexes = this.get( "globalRowQuantileIndexes" );
		var globalOrderedRowCount = this.state.get( "globalOrderedRowCount" );
		var globalOrderedRowQuantile = this.state.get( "globalOrderedRowQuantile" );
		
		var orderedRowCount = globalOrderedRowCount;
		var rowRankingIndexes = globalRowRankingIndexes;
		var rowRankingWeights = globalRowRankingWeights;
		for ( var i = 0; i < orderedRowCount && i < rowRankingIndexes.length; i++ )
			rowPriorities[ rowRankingIndexes[i] ].weights.push( rowRankingWeights[i] );
		
		var orderedRowQuantile = globalOrderedRowQuantile;
		var rowQuantileIndexes = globalRowQuantileIndexes;
		for ( var i = 0; i < orderedRowQuantile; i++ ) {
			var weight = ( 100.0 - i ) / 100.0;
			for ( var j = 0; j < rowQuantileIndexes[i].length; j++ )
				rowPriorities[ rowQuantileIndexes[i][j] ].weights.push( weight );
		}
	}.bind(this);
	var addColumnOrderedRows = function() {
		var columnOrderedRowCounts = this.state.get( "columnOrderedRowCounts" );
		var columnOrderedRowQuantiles = this.state.get( "columnOrderedRowQuantiles" );

		for ( var t = 0; t < allColumnElements.length; t++ ) {
			var element = allColumnElements[ t ];
			var numOrdered = 0;
			
			var orderedRowCount = columnOrderedRowCounts.hasOwnProperty(t) ? columnOrderedRowCounts[t] : 0;
			var rowRankingIndexes = element.rowRankingIndexes;
			var rowRankingWeights = element.rowRankingWeights;
			for ( var i = 0; i < orderedRowCount && i < rowRankingIndexes.length; i++ ) {
				rowPriorities[ rowRankingIndexes[i] ].weights.push( rowRankingWeights[i] );
				numOrdered ++;
			}
			var orderedRowQuantile = columnOrderedRowQuantiles.hasOwnProperty(t) ? columnOrderedRowQuantiles[t] : 0;
			var rowQuantileIndexes = element.rowQuantileIndexes;
			for ( var i = 0; i < orderedRowQuantile; i++ ) {
				var weight = ( 100.0 - i ) / 100.0;
				for ( var j = 0; j < rowQuantileIndexes[i].length; j++ ) {
					rowPriorities[ rowQuantileIndexes[i][j] ].weights.push( weight );
					numOrdered ++;
				}
			}
			if ( numOrdered !== element.numOrdered ) {
				element.numOrdered = numOrdered;
				this.setDirty( "allColumnElements", element.key, "numOrdered" );
				this.__setDirtyModel( "allColumnElements", "numOrdered" );
			}
			if ( orderedRowCount !== element.orderedRowCount ) {
				element.orderedRowCount = orderedRowCount;
				this.setDirty( "allColumnElements", element.key, "orderedRowCount" );
				this.__setDirtyModel( "allColumnElements", "orderedRowCount" );
			}
			if ( orderedRowQuantile !== element.orderedRowQuantile ) {
				element.orderedRowQuantile = orderedRowQuantile;
				this.setDirty( "allColumnElements", element.key, "orderedRowQuantile" );
				this.__setDirtyModel( "allColumnElements", "orderedRowQuantile" );
			}
		}
	}.bind(this);
	var addSelectionOrderedRows = function() {
		var columnSelections = this.state.get( "columnSelections" );
		var selectionOrderedRowCounts = this.state.get( "selectionOrderedRowCounts" );
		var selectionOrderedRowQuantiles = this.state.get( "selectionOrderedRowQuantiles" );

		for ( var t in columnSelections ) {
			var selectionIndex = columnSelections[ t ];
			var element = allColumnElements[ t ];
			var group = allSelectionGroups[ selectionIndex ];
			var numOrdered = 0;
			
			var orderedRowCount = selectionOrderedRowCounts.hasOwnProperty( selectionIndex ) ? selectionOrderedRowCounts[ selectionIndex ] : 0;
			var rowRankingIndexes = element.rowRankingIndexes;
			var rowRankingWeights = element.rowRankingWeights;
			for ( var i = 0; i < orderedRowCount && i < rowRankingIndexes.length; i++ ) {
				rowPriorities[ rowRankingIndexes[i] ].weights.push( rowRankingWeights[i] );
				numOrdered ++;
			}
			var orderedRowQuantile = selectionOrderedRowQuantiles.hasOwnProperty( selectionIndex ) ? selectionOrderedRowQuantiles[ selectionIndex ] : 0;
			var rowQuantileIndexes = element.rowQuantileIndexes;
			for ( var i = 0; i < orderedRowQuantile; i++ ) {
				var weight = ( 100.0 - i ) / 100.0;
				for ( var j = 0; j < rowQuantileIndexes[i].length; j++ ) {
					rowPriorities[ rowQuantileIndexes[i][j] ].weights.push( weight );
					numOrdered ++;
				}
			}
			if ( numOrdered !== group.numOrdered ) {
				group.numOrdered = numOrdered;
				this.setDirty( "allSelectionGroups", group.key, "numOrdered" );
				this.__setDirtyModel( "allSelectionGroups", "numOrdered" );
			}
			if ( orderedRowCount !== group.orderedRowCount ) {
				group.orderedRowCount = orderedRowCount;
				this.setDirty( "allSelectionGroups", group.key, "orderedRowCount" );
				this.__setDirtyModel( "allSelectionGroups", "orderedRowCount" );
			}
			if ( orderedRowQuantile !== group.orderedRowQuantile ) {
				group.orderedRowQuantile = orderedRowQuantile;
				this.setDirty( "allSelectionGroups", group.key, "orderedRowQuantile" );
				this.__setDirtyModel( "allSelectionGroups", "orderedRowQuantile" );
			}
		}
	}.bind(this);
	var addExpansionOrderedRows = function() {
		var columnOrderedRowCounts = this.state.get( "columnOrderedRowCounts" );
		var columnOrderedRowQuantiles = this.state.get( "columnOrderedRowQuantiles" );
		var expansionOrderedRowCount = this.state.get( "expansionOrderedRowCount" );
		var expansionOrderedRowQuantile = this.state.get( "expansionOrderedRowQuantile" );
		var allColumnElements = this.get( "allColumnElements" );
		var columnExpansions = this.state.get( "columnExpansions" );
		
		for ( var t in columnExpansions ) {
			var element = allColumnElements[ t ];
			var numOrdered = 0;

			if ( ! columnOrderedRowCounts.hasOwnProperty(t) ) {
				var orderedRowCount = expansionOrderedRowCount;
				var rowRankingIndexes = element.rowRankingIndexes;
				var rowRankingWeights = element.rowRankingWeights;
				for ( var i = 0; i < orderedRowCount && i < rowRankingIndexes.length; i++ ) {
					rowPriorities[ rowRankingIndexes[i] ].weights.push( rowRankingWeights[i] );
					numOrdered ++;
				}
			}
			if ( ! columnOrderedRowQuantiles.hasOwnProperty(t) ) {
				var orderedRowQuantile = expansionOrderedRowQuantile;
				var rowQuantileIndexes = element.rowQuantileIndexes;
				for ( var i = 0; i < orderedRowQuantile; i++ ) {
					var weight = ( 100.0 - i ) / 100.0;
					for ( var j = 0; j < rowQuantileIndexes[i].length; j++ ) {
						rowPriorities[ rowQuantileIndexes[i][j] ].weights.push( weight );
						numOrdered ++;
					}
				}
			}
		}
	}.bind(this);
	
	var rowAutoOrderingBaseList = this.state.get( "rowAutoOrderingBaseList" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );

	var rowPriorities = new Array( allRowElements.length );
	for ( var s = 0; s < allRowElements.length; s++ ) {
		rowPriorities[s] = { "index": s, "weights" : [] };
	}
	addGlobalOrderedRows();
	addColumnOrderedRows();
	addSelectionOrderedRows();
	addExpansionOrderedRows();
	for ( var s = 0; s < allRowElements.length; s++ ) {
		var weights = rowPriorities[s].weights;
		var scalar = 1.0;
		for ( var i = 0; i < weights.length; i++ ) {
			var weight = weights[i];
			scalar *= ( 1.0 - weight );
		}
		rowPriorities[s].priority = 1.0 - scalar;
	}
	for ( var i = 0; i < rowAutoOrderingBaseList.length; i++ ) {
		var s = rowAutoOrderingBaseList[i];
		rowPriorities[s].priority -= 1e-8 * i / rowAutoOrderingBaseList.length;
	}
	rowPriorities.sort( function(a,b) { return b.priority - a.priority } );
	
	var rowAbsOrdering = new Array( allRowElements.length );
	for ( var s = 0; s < allRowElements.length; s++ )
		rowAbsOrdering[s] = rowPriorities[s].index;
	return rowAbsOrdering;
};

MatrixModel.prototype.__getColumnAutoOrdering = function() {
	var allColumnElements = this.get( "allColumnElements" );
	return _.range( allColumnElements.length );
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.__updateRowPositions = function() {
	if ( this.__isDirtyModel( "rowAbsOrdering" ) || this.__isDirtyModel( "allRowElements", "isVisible" ) )
	{
		var rowAbsOrdering = this.get( "rowAbsOrdering" );
		var allRowElements = this.get( "allRowElements" );
		var rowPositions = this.__interpolateOrderingPositions( allRowElements, rowAbsOrdering );
		this.__setDirtyModelAndValue( "rowPositions", rowPositions );
	}
	if ( this.__isDirtyModel( "rowPositions" ) ) {
		var rowPositions = this.get( "rowPositions" );
		this.__onRowPositions( rowPositions );
	}
};

MatrixModel.prototype.__onRowPositions = function( rowPositions ) {
	var allEntries = this.get( "allEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allRowCrossRefs = this.get( "allRowCrossRefs" );
	
	for ( var n = 0; n < allEntries.length; n++ ) {
		var entry = allEntries[n];
		var rowPosition = rowPositions[ entry.rowIndex ];
		if ( rowPosition !== entry.rowPosition ) {
			entry.rowPosition = rowPosition;
			this.setDirty( "allEntries", entry.key, "rowPosition" );
			this.__setDirtyModel( "allEntries", "rowPosition" );
		}
	}
	for ( var t = 0; t < allRowElements.length; t++ ) {
		var element = allRowElements[t];
		var rowPosition = rowPositions[ t ];
		if ( rowPosition !== element.rowPosition ) {
			element.rowPosition = rowPosition;
			this.setDirty( "allRowElements", element.key, "rowPosition" );
			this.__setDirtyModel( "allRowElements", "rowPosition" );
		}
	}
	for ( var ts = 0; ts < allRowCrossRefs.length; ts++ ) {
		var crossRef = allRowCrossRefs[ts];
		var rowPosition = crossRef.parent.rowPosition;
		if ( rowPosition !== crossRef.rowPosition ) {
			crossRef.rowPosition = rowPosition;
			this.setDirty( "allRowCrossRefs", crossRef.key, "rowPosition" );
			this.__setDirtyModel( "allRowCrossRefs", "rowPosition" );
		}
	}
};

MatrixModel.prototype.__updateColumnPositions = function() {
	if ( this.__isDirtyModel( "columnAbsOrdering" ) || this.__isDirtyModel( "allColumnElements", "isVisible" ) )
	{
		var columnAbsOrdering = this.get( "columnAbsOrdering" );
		var allColumnElements = this.get( "allColumnElements" );
		var columnPositions = this.__interpolateOrderingPositions( allColumnElements, columnAbsOrdering );
		this.__setDirtyModelAndValue( "columnPositions", columnPositions );
	}
	if ( this.__isDirtyModel( "columnPositions" ) ) {
		var columnPositions = this.get( "columnPositions" );
		this.__onColumnPositions( columnPositions );
	}
	if ( this.__isDirtyModel( "columnPositions" ) || this.__isDirtyState( "columnExpansions" ) ) {
		var columnPositions = this.get( "columnPositions" );
		var columnExpansions = this.state.get( "columnExpansions" );
		var thisColumnExpansion = _.keys( columnExpansions ).map( function(d) { return parseInt(d) } )[0];	// Take only the first highlight
		this.__onExpansionColumnPosition( columnPositions, thisColumnExpansion );
	}
};

MatrixModel.prototype.__onColumnPositions = function( columnPositions ) {
	var allEntries = this.get( "allEntries" );
	var allColumnElements = this.get( "allColumnElements" );
	var allColumnCrossRefs = this.get( "allColumnCrossRefs" );
	
	for ( var n = 0; n < allEntries.length; n++ ) {
		var entry = allEntries[n];
		var columnPosition = columnPositions[ entry.columnIndex ];
		if ( columnPosition !== entry.columnPosition ) {
			entry.columnPosition = columnPosition;
			this.setDirty( "allEntries", entry.key, "columnPosition" );
			this.__setDirtyModel( "allEntries", "columnPosition" );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		var columnPosition = columnPositions[ t ];
		if ( columnPosition !== element.columnPosition ) {
			element.columnPosition = columnPosition;
			this.setDirty( "allColumnElements", element.key, "columnPosition" );
			this.__setDirtyModel( "allColumnElements", "columnPosition" );
		}
	}
	for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
		var crossRef = allColumnCrossRefs[ts];
		var columnPosition = crossRef.parent.columnPosition;
		if ( columnPosition !== crossRef.columnPosition ) {
			crossRef.columnPosition = columnPosition;
			this.setDirty( "allColumnCrossRefs", crossRef.key, "columnPosition" );
			this.__setDirtyModel( "allColumnCrossRefs", "columnPosition" );
		}
	}
};

MatrixModel.prototype.__onExpansionColumnPosition = function( columnPositions, thisColumnExpansion ) {
	var expansionColumnPosition = undefined;
	if ( thisColumnExpansion !== undefined ) {
		expansionColumnPosition = columnPositions[ thisColumnExpansion ];
	}
	if ( expansionColumnPosition !== this.get( "expansionColumnPosition" ) ) {
		this.set( "expansionColumnPosition", expansionColumnPosition );
		this.setDirty( "expansionColumnPosition" );
	}
};


/**
 * Smooth interpolation of element positions.
 * Invisible elements are placed in between visible elements, instead of assigned arbitrary
 * position such as -1 which causes undesirable animated transitions.
 * @inner
 **/
MatrixModel.prototype.__interpolateOrderingPositions = function( elements, ordering ) {
	// Prepare the data structure for storing computed positions.
	var positions = new Array( elements.length );
	for ( var i = 0; i < elements.length; i++ )
		positions[i] = undefined;

	// Identify the list of visible elements and their indexes.
	var subOrdering = [];
	var subIndexes = [];
	for ( var i = 0; i < elements.length; i++ ) {
		var d = ordering[i];
		if ( elements[d].isVisible ) {
			subOrdering.push(d);
			subIndexes.push(i);
		}
	}

	// Assign all visible elements a position from 0 to N'.
	for ( var i = 0; i < subOrdering.length; i++ )
		positions[ subOrdering[i] ] = i;

	return positions;
};
