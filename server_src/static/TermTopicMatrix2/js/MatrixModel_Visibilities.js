MatrixModel.prototype.__updateVisibilities = function() {
	var resetAllVisibilities = function() {
		for ( var s = 0; s < allRowElements.length; s++ ) {
			var element = allRowElements[s];
			rowVisibilities[s] = ( element.isAdmitted && !element.isExcluded ) || ( !element.isAdmitted && element.isIncluded );
		}
		for ( var t = 0; t < allColumnElements.length; t++ ) {
			var element = allColumnElements[t];
			columnVisibilities[t] = ( element.isAdmitted && !element.isExcluded ) || ( !element.isAdmitted && element.isIncluded );
		}
	}.bind(this);
	var addGlobalVisibleRows = function() {
		var globalRowRankingIndexes = this.get( "globalRowRankingIndexes" );
		var globalRowQuantileIndexes = this.get( "globalRowQuantileIndexes" );
		var globalVisibleRowCount = this.state.get( "globalVisibleRowCount" );
		var globalVisibleRowQuantile = this.state.get( "globalVisibleRowQuantile" );

		var visibleRowCount = globalVisibleRowCount;
		var rowRankingIndexes = globalRowRankingIndexes;
		for ( var i = 0; i < visibleRowCount && i < rowRankingIndexes.length; i++ )
			rowVisibilities[ rowRankingIndexes[i] ] = true;
			
		var visibleRowQuantile = globalVisibleRowQuantile;
		var rowQuantileIndexes = globalRowQuantileIndexes;
		for ( var i = 0; i < visibleRowQuantile; i++ )
			for ( var j = 0; j < rowQuantileIndexes[i].length; j++ )
				rowVisibilities[ rowQuantileIndexes[i][j] ] = true;
	}.bind(this);
	var addColumnVisibleRows = function() {
		var columnVisibleRowCounts = this.state.get( "columnVisibleRowCounts" );
		var columnVisibleRowQuantiles = this.state.get( "columnVisibleRowQuantiles" );

		for ( var t = 0; t < allColumnElements.length; t++ ) {
			var element = allColumnElements[ t ];
			var numVisibles = 0;
			
			var visibleRowCount = columnVisibleRowCounts.hasOwnProperty(t) ? columnVisibleRowCounts[t] : 0;
			var rowRankingIndexes = element.rowRankingIndexes;
			for ( var i = 0; i < visibleRowCount && i < rowRankingIndexes.length; i++ ) {
				rowVisibilities[ rowRankingIndexes[i] ] = true;
				numVisibles ++;
			}
			var visibleRowQuantile = columnVisibleRowQuantiles.hasOwnProperty(t) ? columnVisibleRowQuantiles[t] : 0;
			var rowQuantileIndexes = element.rowQuantileIndexes;
			for ( var i = 0; i < visibleRowQuantile; i++ )
				for ( var j = 0; j < rowQuantileIndexes[i].length; j++ ) {
					rowVisibilities[ rowQuantileIndexes[i][j] ] = true;
					numVisibles ++;
				}
			if ( numVisibles !== element.numVisibles ) {
				element.numVisibles = numVisibles;
				this.setDirty( "allColumnElements", element.key, "numVisibles" );
				this.__setDirtyModel( "allColumnElements", "numVisibles" );
			}
			if ( visibleRowCount !== element.visibleRowCount ) {
				element.visibleRowCount = visibleRowCount;
				this.setDirty( "allColumnElements", element.key, "visibleRowCount" );
				this.__setDirtyModel( "allColumnElements", "visibleRowCount" );
			}
			if ( visibleRowQuantile !== element.visibleRowQuantile ) {
				element.visibleRowQuantile = visibleRowQuantile;
				this.setDirty( "allColumnElements", element.key, "visibleRowQuantile" );
				this.__setDirtyModel( "allColumnElements", "visibleRowQuantile" );
			}
		}
	}.bind(this);
	var addSelectionVisibleRows = function() {
		var columnSelections = this.state.get( "columnSelections" );
		var selectionVisibleRowCounts = this.state.get( "selectionVisibleRowCounts" );
		var selectionVisibleRowQuantiles = this.state.get( "selectionVisibleRowQuantiles" );

		for ( var t in columnSelections ) {
			var selectionIndex = columnSelections[ t ];
			var element = allColumnElements[ t ];
			var group = allSelectionGroups[ selectionIndex ];
			var numVisibles = 0;
			
			var visibleRowCount = selectionVisibleRowCounts.hasOwnProperty( selectionIndex ) ? selectionVisibleRowCounts[ selectionIndex ] : 0;
			var rowRankingIndexes = element.rowRankingIndexes;
			for ( var i = 0; i < visibleRowCount && i < rowRankingIndexes.length; i++ ) {
				rowVisibilities[ rowRankingIndexes[i] ] = true;
				numVisibles ++;
			}
			var visibleRowQuantile = selectionVisibleRowQuantiles.hasOwnProperty( selectionIndex ) ? selectionVisibleRowQuantiles[ selectionIndex ] : 0;
			var rowQuantileIndexes = element.rowQuantileIndexes;
			for ( var i = 0; i < visibleRowQuantile; i++ )
				for ( var j = 0; j < rowQuantileIndexes[i].length; j++ ) {
					rowVisibilities[ rowQuantileIndexes[i][j] ] = true;
					numVisibles ++;
				}
			if ( numVisibles !== group.numVisibles ) {
				group.numVisibles = numVisibles;
				this.setDirty( "allSelectionGroups", group.key, "numVisibles" );
				this.__setDirtyModel( "allSelectionGroups", "numVisibles" );
			}
			if ( visibleRowCount !== group.visibleRowCount ) {
				group.visibleRowCount = visibleRowCount;
				this.setDirty( "allSelectionGroups", group.key, "visibleRowCount" );
				this.__setDirtyModel( "allSelectionGroups", "visibleRowCount" );
			}
			if ( visibleRowQuantile !== group.visibleRowQuantile ) {
				group.visibleRowQuantile = visibleRowQuantile;
				this.setDirty( "allSelectionGroups", group.key, "visibleRowQuantile" );
				this.__setDirtyModel( "allSelectionGroups", "visibleRowQuantile" );
			}
		}
	}.bind(this);
	var addExpansionVisibleRows = function() {
		var columnExpansions = this.state.get( "columnExpansions" );
		var columnVisibleRowCounts = this.state.get( "columnVisibleRowCounts" );
		var columnVisibleRowQuantiles = this.state.get( "columnVisibleRowQuantiles" );
		var expansionVisibleRowCount = this.state.get( "expansionVisibleRowCount" );
		var expansionVisibleRowQuantile = this.state.get( "expansionVisibleRowQuantile" );

		for ( var t in columnExpansions ) {
			var element = allColumnElements[ t ];
			var numVisibles = 0;
			
			var visibleRowCount = columnVisibleRowCounts.hasOwnProperty(t) ? columnVisibleRowCounts[t] : expansionVisibleRowCount;
			var rowRankingIndexes = element.rowRankingIndexes;
			for ( var i = 0; i < visibleRowCount && i < rowRankingIndexes.length; i++ ) {
				rowVisibilities[ rowRankingIndexes[i] ] = true;
				numVisibles ++;
			}
				
			var visibleRowQuantile = columnVisibleRowQuantiles.hasOwnProperty(t) ? columnVisibleRowQuantiles[t] : expansionVisibleRowQuantile;
			var rowQuantileIndexes = element.rowQuantileIndexes;
			for ( var i = 0; i < visibleRowQuantile; i++ )
				for ( var j = 0; j < rowQuantileIndexes[i].length; j++ ) {
					rowVisibilities[ rowQuantileIndexes[i][j] ] = true;
					numVisibles ++;
				}
		}
	}.bind(this);
	var addPromotedRows = function() {
		for ( var s = 0; s < allRowElements.length; s++ ) {
			var element = allRowElements[ s ];
			if ( element.numPromoted > 0 )
				rowVisibilities[ s ] = true;
		}
	}.bind(this);
	var addUserVisibleRows = function() {
		var rowUserDefinedVisibilities = this.state.get( "rowUserDefinedVisibilities" );
		for ( var s in rowUserDefinedVisibilities )
			rowVisibilities[ s ] = rowUserDefinedVisibilities[ s ];
	}.bind(this);

	var allEntries = this.get( "allEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );
	var allRowCrossRefs = this.get( "allRowCrossRefs" );
	var allColumnCrossRefs = this.get( "allColumnCrossRefs" );
	var allSelectionGroups = this.get( "allSelectionGroups" );
	var rowVisibilities = new Array( allRowElements.length );
	var columnVisibilities = new Array( allColumnElements.length );

	resetAllVisibilities();
	addGlobalVisibleRows();
	addColumnVisibleRows();
	addExpansionVisibleRows();
	addSelectionVisibleRows();
	addPromotedRows();
	addUserVisibleRows();

	for ( var n = 0; n < allEntries.length; n++ ) {
		var entry = allEntries[n];
		var s = entry.rowIndex;
		var t = entry.columnIndex;
		var wasVisible = ( entry.isVisible === true );
		var isVisible = ( rowVisibilities[s] && columnVisibilities[t] );
		entry.isEnter = ( !wasVisible && isVisible );
		entry.isStay = ( wasVisible && isVisible );
		entry.isExit = ( wasVisible && !isVisible );
		if ( isVisible !== entry.isVisible ) {
			entry.isVisible = isVisible;
			this.setDirty( "allEntries", entry.key, "isVisible" );
			this.__setDirtyModel( "allEntries", "isVisible" );
		}
	}
	for ( var s = 0; s < allRowElements.length; s++ ) {
		var element = allRowElements[s];
		var wasVisible = ( element.isVisible === true );
		var isVisible = ( rowVisibilities[s] );
		element.isEnter = ( !wasVisible && isVisible );
		element.isStay = ( wasVisible && isVisible );
		element.isExit = ( wasVisible && !isVisible );
		if ( isVisible !== element.isVisible ) {
			element.isVisible = isVisible;
			this.setDirty( "allRowElements", element.key, "isVisible" );
			this.__setDirtyModel( "allRowElements", "isVisible" );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		var wasVisible = ( element.isVisible === true );
		var isVisible = ( columnVisibilities[t] );
		element.isEnter = ( !wasVisible && isVisible );
		element.isStay = ( wasVisible && isVisible );
		element.isExit = ( wasVisible && !isVisible );
		if ( isVisible !== element.isVisible ) {
			element.isVisible = isVisible;
			this.setDirty( "allColumnElements", element.key, "isVisible" );
			this.__setDirtyModel( "allColumnElements", "isVisible" );
		}
	}
	for ( var st = 0; st < allRowCrossRefs.length; st++ ) {
		var crossRef = allRowCrossRefs[st];
		var wasVisible = ( crossRef.isVisible === true );
		var s = crossRef.rowIndex;
		var t = crossRef.columnIndex;
		var isVisible = ( rowVisibilities[s] && columnVisibilities[t] );
		crossRef.isEnter = ( !wasVisible && isVisible );
		crossRef.isStay = ( wasVisible && isVisible );
		crossRef.isExit = ( wasVisible && !isVisible );
		if ( isVisible !== crossRef.isVisible ) {
			crossRef.isVisible = isVisible;
			this.setDirty( "allRowCrossRefs", crossRef.key, "isVisible" );
			this.__setDirtyModel( "allRowCrossRefs", "isVisible" );
		}
	}
	for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
		var crossRef = allColumnCrossRefs[ts];
		var wasVisible = ( crossRef.isVisible === true );
		var s = crossRef.rowIndex;
		var t = crossRef.columnIndex;
		var isVisible = ( rowVisibilities[s] && columnVisibilities[t] );
		crossRef.isEnter = ( !wasVisible && isVisible );
		crossRef.isStay = ( wasVisible && isVisible );
		crossRef.isExit = ( wasVisible && !isVisible );
		if ( isVisible !== crossRef.isVisible ) {
			crossRef.isVisible = isVisible;
			this.setDirty( "allColumnCrossRefs", crossRef.key, "isVisible" );
			this.__setDirtyModel( "allColumnCrossRefs", "isVisible" );
		}
	}
	
	this.__setDirtyModel( "allEntries", [ "isEnter", "isStay", "isExit" ] );
	this.__setDirtyModel( "allRowElements", [ "isEnter", "isStay", "isExit" ] );
	this.__setDirtyModel( "allColumnElements", [ "isEnter", "isStay", "isExit" ] );
	this.__setDirtyModel( "allRowCrossRefs", [ "isEnter", "isStay", "isExit" ] );
	this.__setDirtyModel( "allColumnCrossRefs", [ "isEnter", "isStay", "isExit" ] );
};
