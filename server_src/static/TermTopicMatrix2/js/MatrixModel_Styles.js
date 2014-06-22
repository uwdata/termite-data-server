MatrixModel.prototype.__updateSelections = function() {
	if ( this.__isDirtyState( "columnSelections" ) ) {
		var columnSelections = this.state.get( "columnSelections" );
		this.__onColumnSelections_shortcutLoops( columnSelections );
	}
};

MatrixModel.prototype.__onColumnSelections_exhaustiveLoops = function( columnSelections ) {
	var allEntries = this.get( "allEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );
	var allRowCrossRefs = this.get( "allRowCrossRefs" );
	var allColumnCrossRefs = this.get( "allColumnCrossRefs" );
	
	for ( var n = 0; n < allEntries.length; n++ ) {
		var entry = allEntries[n];
		var selectionIndex = columnSelections[ entry.columnIndex ];
		var isSelected = ( selectionIndex >= 0 );
		if ( selectionIndex !== entry.selectionIndex || isSelected !== entry.isSelected ) {
			entry.selectionIndex = selectionIndex;
			entry.isSelected = isSelected;
			this.setDirty( "allEntries", entry.key, [ "isSelected", "selectionIndex" ] );
			this.__setDirtyModel( "allEntries", [ "isSelected", "selectionIndex" ] );
		}
	}
	for ( var s = 0; s < allRowElements.length; s++ ) {
		var element = allRowElements[s];
		var selectionIndex = undefined;
		var isSelected = false;
		if ( selectionIndex !== element.selectionIndex || isSelected !== element.isSelected ) {
			element.selectionIndex = selectionIndex;
			element.isSelected = isSelected;
			this.setDirty( "allRowElements", element.key, [ "isSelected", "selectionIndex" ] );
			this.__setDirtyModel( "allRowElements", [ "isSelected", "selectionIndex" ] );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		var selectionIndex = columnSelections[ t ];
		var isSelected = ( selectionIndex >= 0 );
		if ( selectionIndex !== element.selectionIndex || isSelected !== element.isSelected ) {
			element.selectionIndex = selectionIndex;
			element.isSelected = isSelected;
			this.setDirty( "allColumnElements", element.key, [ "isSelected", "selectionIndex" ] );
			this.__setDirtyModel( "allColumnElements", [ "isSelected", "selectionIndex" ] );
		}
	}
	for ( var st = 0; st < allRowCrossRefs.length; st++ ) {
		var crossRef = allRowCrossRefs[st];
		var selectionIndex = columnSelections[ crossRef.columnIndex ];
		var isSelected = ( selectionIndex >= 0 );
		if ( selectionIndex !== crossRef.selectionIndex || isSelected !== crossRef.isSelected ) {
			crossRef.selectionIndex = selectionIndex;
			crossRef.isSelected = isSelected;
			this.setDirty( "allRowCrossRefs", crossRef.key, [ "isSelected", "selectionIndex" ] );
			this.__setDirtyModel( "allRowCrossRefs", [ "isSelected", "selectionIndex" ] );
		}
	}
	for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
		var crossRef = allColumnCrossRefs[ts];
		var selectionIndex = undefined;
		var isSelected = false;
		if ( selectionIndex !== crossRef.selectionIndex || isSelected !== crossRef.isSelected ) {
			crossRef.selectionIndex = selectionIndex;
			crossRef.isSelected = isSelected;
			this.setDirty( "allColumnCrossRefs", crossRef.key, [ "isSelected", "selectionIndex" ] );
			this.__setDirtyModel( "allColumnCrossRefs", [ "isSelected", "selectionIndex" ] );
		}
	}
};

MatrixModel.prototype.__onColumnSelections_shortcutLoops = function( columnSelections ) {
	var hashEntries = this.get( "hashEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );
	var hashRowCrossRefs = this.get( "hashRowCrossRefs" );
	var allColumnCrossRefs = this.get( "allColumnCrossRefs" );
	var ss = this.__rowIndexes();
	var tt = this.__columnIndexes( this.__getDirtyState( "columnSelections" ) );
	
	for ( var j = 0; j < tt.length; j++ ) {
		var t = tt[j];
		var selectionIndex = columnSelections[ t ];
		var isSelected = ( selectionIndex >= 0 );
		for ( var i = 0; i < ss.length; i++ ) {
			var s = ss[i];
			var key = s + ":" + t;
			if ( hashEntries.hasOwnProperty(key) ) {
				var entry = hashEntries[ key ];
				if ( selectionIndex !== entry.selectionIndex || isSelected !== entry.isSelected ) {
					entry.selectionIndex = selectionIndex;
					entry.isSelected = isSelected;
					this.setDirty( "allEntries", entry.key, [ "isSelected", "selectionIndex" ] );
					this.__setDirtyModel( "allEntries", [ "isSelected", "selectionIndex" ] );
				}
			}
		}
	}
	for ( var s = 0; s < allRowElements.length; s++ ) {
		var element = allRowElements[s];
		var selectionIndex = undefined;
		var isSelected = false;
		if ( selectionIndex !== element.selectionIndex || isSelected !== element.isSelected ) {
			element.selectionIndex = selectionIndex;
			element.isSelected = isSelected;
			this.setDirty( "allRowElements", element.key, [ "isSelected", "selectionIndex" ] );
			this.__setDirtyModel( "allRowElements", [ "isSelected", "selectionIndex" ] );
		}
	}
	for ( var j = 0; j < tt.length; j++ ) {
		var t = tt[j];
		var element = allColumnElements[ t ];
		var selectionIndex = columnSelections[ t ];
		var isSelected = ( selectionIndex >= 0 );
		if ( selectionIndex !== element.selectionIndex || isSelected !== element.isSelected ) {
			element.selectionIndex = selectionIndex;
			element.isSelected = isSelected;
			this.setDirty( "allColumnElements", element.key, [ "isSelected", "selectionIndex" ] );
			this.__setDirtyModel( "allColumnElements", [ "isSelected", "selectionIndex" ] );
		}
	}
	for ( var j = 0; j < tt.length; j++ ) {
		var t = tt[j];
		var selectionIndex = columnSelections[ t ];
		var isSelected = ( selectionIndex >= 0 );
		for ( var i = 0; i < ss.length; i++ ) {
			var s = ss[i];
			var key = s + ":" + t;
			if ( hashRowCrossRefs.hasOwnProperty(key) ) {
				var crossRef = hashRowCrossRefs[ key ];
				if ( selectionIndex !== crossRef.selectionIndex || isSelected !== crossRef.isSelected ) {
					crossRef.selectionIndex = selectionIndex;
					crossRef.isSelected = isSelected;
					this.setDirty( "allRowCrossRefs", crossRef.key, [ "isSelected", "selectionIndex" ] );
					this.__setDirtyModel( "allRowCrossRefs", [ "isSelected", "selectionIndex" ] );
				}
			}
		}
	}
	for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
		var crossRef = allColumnCrossRefs[ts];
		var selectionIndex = undefined;
		var isSelected = false;
		if ( selectionIndex !== crossRef.selectionIndex || isSelected !== crossRef.isSelected ) {
			crossRef.selectionIndex = selectionIndex;
			crossRef.isSelected = isSelected;
			this.setDirty( "allColumnCrossRefs", crossRef.key, [ "isSelected", "selectionIndex" ] );
			this.__setDirtyModel( "allColumnCrossRefs", [ "isSelected", "selectionIndex" ] );
		}
	}
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.__updateHighlights = function() {
	if ( this.__isDirtyState( "rowHighlights" ) || this.__isDirtyState( "columnHighlights" ) || this.__isDirtyState( "entryHighlights" ) ||
		 this.__isDirtyModel( "allColumnElements", [ "rowHighlights", "isSeleted", "selectionIndex" ] ) )
	{
		var rowHighlights = this.state.get( "rowHighlights" );
		var columnHighlights = this.state.get( "columnHighlights" );
		var entryHighlights = this.state.get( "entryHighlights" );
		var thisRowHighlight = _.keys( rowHighlights ).map( function(d) { return parseInt(d) } )[0];		// Take only the first highlight
		var thisColumnHighlight = _.keys( columnHighlights ).map( function(d) { return parseInt(d) } )[0];	// Take only the first highlight
		var thisEntryHighlight = _.keys( entryHighlights )[0];												// Take only the first highlight

		if ( thisRowHighlight !== undefined )
			this.__onRowHighlights_shortcutLoops( thisRowHighlight );
		else if ( thisColumnHighlight !== undefined )
			this.__onColumnHighlights_exhaustiveLoops( thisColumnHighlight );
		else if ( thisEntryHighlight !== undefined )
			this.__onEntryHighlights_shortcutLoops( thisEntryHighlight );
		else
			this.__onNoHighlights_exhaustiveLoops();
	}
};

MatrixModel.prototype.__onRowHighlights_exhaustiveLoops = function( thisRowHighlight ) {
	var allEntries = this.get( "allEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );
	var allRowCrossRefs = this.get( "allRowCrossRefs" );
	var allColumnCrossRefs = this.get( "allColumnCrossRefs" );
	var thisRowElement = allRowElements[ thisRowHighlight ];

	var highlightSelectionIndex = undefined;
	if ( thisRowElement.isSelected ) {
		highlightSelectionIndex = thisRowElement.selectionIndex;
	}
	if ( highlightSelectionIndex !== this.get( "highlightSelectionIndex" ) ) {
		this.set( "highlightSelectionIndex", highlightSelectionIndex );
		this.setDirty( "highlightSelectionIndex" );
	}

	for ( var n = 0; n < allEntries.length; n++ ) {
		var entry = allEntries[n];
		var isHighlighted = ( entry.rowIndex === thisRowHighlight );
		if ( isHighlighted !== entry.isHighlighted ) {
			entry.isHighlighted = isHighlighted;
			this.setDirty( "allEntries", entry.key, "isHighlighted" );
			this.__setDirtyModel( "allEntries", "isHighlighted" );
		}
	}
	for ( var s = 0; s < allRowElements.length; s++ ) {
		var element = allRowElements[s];
		var isHighlighted = ( s === thisRowHighlight );
		if ( isHighlighted !== element.isHighlighted ) {
			element.isHighlighted = isHighlighted;
			this.setDirty( "allRowElements", element.key, "isHighlighted" );
			this.__setDirtyModel( "allRowElements", "isHighlighted" );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		var isHighlighted = false;
		if ( isHighlighted !== element.isHighlighted ) {
			element.isHighlighted = isHighlighted;
			this.setDirty( "allColumnElements", element.key, "isHighlighted" );
			this.__setDirtyModel( "allColumnElements", "isHighlighted" );
		}
	}
	for ( var st = 0; st < allRowCrossRefs.length; st++ ) {
		var crossRef = allRowCrossRefs[st];
		var isHighlighted = false;
		if ( isHighlighted !== crossRef.isHighlighted ) {
			crossRef.isHighlighted = isHighlighted;
			this.setDirty( "AllRowCrossRefs", crossRef.key, "isHighlighted" );
			this.__setDirtyModel( "allRowCrossRefs", "isHighlighted" );
		}
	}
	for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
		var crossRef = allColumnCrossRefs[ts];
		var isHighlighted = ( crossRef.rowIndex === thisRowHighlight );
		if ( isHighlighted !== crossRef.isHighlighted ) {
			crossRef.isHighlighted = isHighlighted;
			this.setDirty( "allColumnCrossRefs", crossRef.key, "isHighlighted" );
			this.__setDirtyModel( "allColumnCrossRefs", "isHighlighted" );
		}
	}
};

MatrixModel.prototype.__onRowHighlights_shortcutLoops = function( thisRowHighlight ) {
	var hashEntries = this.get( "hashEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );
	var allRowCrossRefs = this.get( "allRowCrossRefs" );
	var hashColumnCrossRefs = this.get( "hashColumnCrossRefs" );
	var thisRowElement = allRowElements[ thisRowHighlight ];

	var highlightSelectionIndex = undefined;
	if ( thisRowElement.isSelected ) {
		highlightSelectionIndex = thisRowElement.selectionIndex;
	}
	if ( highlightSelectionIndex !== this.get( "highlightSelectionIndex" ) ) {
		this.set( "highlightSelectionIndex", highlightSelectionIndex );
		this.setDirty( "highlightSelectionIndex" );
	}

	var ss = this.__rowIndexes( this.__getDirtyState( "rowHighlights" ) );
	var tt = this.__columnIndexes();
	for ( var i = 0; i < ss.length; i++ ) {
		var s = ss[i];
		var isHighlighted = ( s === thisRowHighlight );
		for ( var j = 0; j < tt.length; j++ ) {
			var t = tt[j];
			var key = s + ":" + t;
			if ( hashEntries.hasOwnProperty(key) ) {
				var entry = hashEntries[key];
				if ( isHighlighted !== entry.isHighlighted ) {
					entry.isHighlighted = isHighlighted;
					this.setDirty( "allEntries", entry.key, "isHighlighted" );
					this.__setDirtyModel( "allEntries", "isHighlighted" );
				}
			}
		}
	}
	for ( var i = 0; i < ss.length; i++ ) {
		var s = ss[i];
		var isHighlighted = ( s === thisRowHighlight );
		var element = allRowElements[s];
		if ( isHighlighted !== element.isHighlighted ) {
			element.isHighlighted = isHighlighted;
			this.setDirty( "allRowElements", element.key, "isHighlighted" );
			this.__setDirtyModel( "allRowElements", "isHighlighted" );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		var isHighlighted = false;
		if ( isHighlighted !== element.isHighlighted ) {
			element.isHighlighted = isHighlighted;
			this.setDirty( "allColumnElements", element.key, "isHighlighted" );
			this.__setDirtyModel( "allColumnElements", "isHighlighted" );
		}
	}
	for ( var st = 0; st < allRowCrossRefs.length; st++ ) {
		var crossRef = allRowCrossRefs[st];
		var isHighlighted = false;
		if ( isHighlighted !== crossRef.isHighlighted ) {
			crossRef.isHighlighted = isHighlighted;
			this.setDirty( "AllRowCrossRefs", crossRef.key, "isHighlighted" );
			this.__setDirtyModel( "allRowCrossRefs", "isHighlighted" );
		}
	}
	for ( var i = 0; i < ss.length; i++ ) {
		var s = ss[i];
		var isHighlighted = ( s === thisRowHighlight );
		for ( var j = 0; j < tt.length; j++ ) {
			var t = tt[j];
			var key = s + ":" + t;
			if ( hashColumnCrossRefs.hasOwnProperty(key) ) {
				var crossRef = hashColumnCrossRefs[key];
				if ( isHighlighted !== crossRef.isHighlighted ) {
					crossRef.isHighlighted = isHighlighted;
					this.setDirty( "allColumnCrossRefs", crossRef.key, "isHighlighted" );
					this.__setDirtyModel( "allColumnCrossRefs", "isHighlighted" );
				}
			}
		}
	}
};

MatrixModel.prototype.__onColumnHighlights_exhaustiveLoops = function( thisColumnHighlight ) {
	var allEntries = this.get( "allEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );
	var allRowCrossRefs = this.get( "allRowCrossRefs" );
	var allColumnCrossRefs = this.get( "allColumnCrossRefs" );
	var thisColumnElement = allColumnElements[ thisColumnHighlight ];
	var rowHighlights = thisColumnElement.rowHighlights;
	
	var highlightSelectionIndex = undefined;
	if ( thisColumnElement.isSelected ) {
		highlightSelectionIndex = thisColumnElement.selectionIndex;
	}
	if ( highlightSelectionIndex !== this.get( "highlightSelectionIndex" ) ) {
		this.set( "highlightSelectionIndex", highlightSelectionIndex );
		this.setDirty( "highlightSelectionIndex" );
	}

	for ( var n = 0; n < allEntries.length; n++ ) {
		var entry = allEntries[n];
		var isHighlighted = ( rowHighlights.hasOwnProperty( entry.rowIndex ) || entry.columnIndex === thisColumnHighlight );
		if ( isHighlighted !== entry.isHighlighted ) {
			entry.isHighlighted = isHighlighted;
			this.setDirty( "allEntries", entry.key, "isHighlighted" );
			this.__setDirtyModel( "allEntries", "isHighlighted" );
		}
	}
	for ( var s = 0; s < allRowElements.length; s++ ) {
		var element = allRowElements[s];
		var isHighlighted = ( rowHighlights.hasOwnProperty( s ) );
		if ( isHighlighted !== element.isHighlighted ) {
			element.isHighlighted = isHighlighted;
			this.setDirty( "allRowElements", element.key, "isHighlighted" );
			this.__setDirtyModel( "allRowElements", "isHighlighted" );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		var isHighlighted = ( t === thisColumnHighlight );
		if ( isHighlighted !== element.isHighlighted ) {
			element.isHighlighted = isHighlighted;
			this.setDirty( "allColumnElements", element.key, "isHighlighted" );
			this.__setDirtyModel( "allColumnElements", "isHighlighted" );
		}
	}
	for ( var st = 0; st < allRowCrossRefs.length; st++ ) {
		var crossRef = allRowCrossRefs[st];
		var isHighlighted = ( crossRef.columnIndex === thisColumnHighlight );
		if ( isHighlighted !== crossRef.isHighlighted ) {
			crossRef.isHighlighted = isHighlighted;
			this.setDirty( "allRowCrossRefs", crossRef.key, "isHighlighted" );
			this.__setDirtyModel( "allRowCrossRefs", "isHighlighted" );
		}				
	}
	for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
		var crossRef = allColumnCrossRefs[ts];
		var isHighlighted = ( rowHighlights.hasOwnProperty( crossRef.rowIndex ) );
		if ( isHighlighted !== crossRef.isHighlighted ) {
			crossRef.isHighlighted = isHighlighted;
			this.setDirty( "allColumnCrossRefs", crossRef.key, "isHighlighted" );
			this.__setDirtyModel( "allColumnCrossRefs", "isHighlighted" );
		}
	}
};

MatrixModel.prototype.__onEntryHighlights_exhaustiveLoops = function( thisEntryHighlight ) {
	var allEntries = this.get( "allEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );
	var allRowCrossRefs = this.get( "allRowCrossRefs" );
	var allColumnCrossRefs = this.get( "allColumnCrossRefs" );
	var indexes = thisEntryHighlight.split( ":" );
	var thisRowHighlight = parseInt( indexes[0] );
	var thisColumnHighlight = parseInt( indexes[1] );
	var thisColumnElement = allColumnElements[ thisColumnHighlight ];

	var highlightSelectionIndex = undefined;
	if ( thisColumnElement.isSelected ) {
		highlightSelectionIndex = thisColumnElement.selectionIndex;
	}
	if ( highlightSelectionIndex !== this.get( "highlightSelectionIndex" ) ) {
		this.set( "highlightSelectionIndex", highlightSelectionIndex );
		this.setDirty( "highlightSelectionIndex" );
	}

	for ( var n = 0; n < allEntries.length; n++ ) {
		var entry = allEntries[n];
		var isHighlighted = ( entry.key === thisEntryHighlight );
		if ( isHighlighted !== entry.isHighlighted ) {
			entry.isHighlighted = isHighlighted;
			this.setDirty( "allEntries", entry.key, "isHighlighted" );
			this.__setDirtyModel( "allEntries", "isHighlighted" );
		}
	}
	for ( var s = 0; s < allRowElements.length; s++ ) {
		var element = allRowElements[s];
		var isHighlighted = ( s === thisRowHighlight );
		if ( isHighlighted !== element.isHighlighted ) {
			element.isHighlighted = isHighlighted;
			this.setDirty( "allRowElements", element.key, "isHighlighted" );
			this.__setDirtyModel( "allRowElements", "isHighlighted" );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		var isHighlighted = ( t === thisColumnHighlight );
		if ( isHighlighted !== element.isHighlighted ) {
			element.isHighlighted = isHighlighted;
			this.setDirty( "allColumnElements", element.key, "isHighlighted" );
			this.__setDirtyModel( "allColumnElements", "isHighlighted" );
		}
	}
	for ( var st = 0; st < allRowCrossRefs.length; st++ ) {
		var crossRef = allRowCrossRefs[st];
		var isHighlighted = ( crossRef.key === thisEntryHighlight );
		if ( isHighlighted !== crossRef.isHighlighted ) {
			crossRef.isHighlighted = isHighlighted;
			this.setDirty( "allRowCrossRefs", crossRef.key, "isHighlighted" );
			this.__setDirtyModel( "allRowCrossRefs", "isHighlighted" );
		}
	}
	for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
		var crossRef = allColumnCrossRefs[ts];
		var isHighlighted = ( crossRef.key === thisEntryHighlight );
		if ( isHighlighted !== crossRef.isHighlighted ) {
			crossRef.isHighlighted = isHighlighted;
			this.setDirty( "allColumnCrossRefs", crossRef.key, "isHighlighted" );
			this.__setDirtyModel( "allColumnCrossRefs", "isHighlighted" );
		}
	}
};

MatrixModel.prototype.__onEntryHighlights_shortcutLoops = function( thisEntryHighlight ) {
	var hashEntries = this.get( "hashEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );
	var hashRowCrossRefs = this.get( "hashRowCrossRefs" );
	var hashColumnCrossRefs = this.get( "hashColumnCrossRefs" );
	var indexes = thisEntryHighlight.split( ":" );
	var thisRowHighlight = parseInt( indexes[0] );
	var thisColumnHighlight = parseInt( indexes[1] );
	var thisColumnElement = allColumnElements[ thisColumnHighlight ];

	var highlightSelectionIndex = undefined;
	if ( thisColumnElement.isSelected ) {
		highlightSelectionIndex = thisColumnElement.selectionIndex;
	}
	if ( highlightSelectionIndex !== this.get( "highlightSelectionIndex" ) ) {
		this.set( "highlightSelectionIndex", highlightSelectionIndex );
		this.setDirty( "highlightSelectionIndex" );
	}
	
	var entryHighlights = this.__getDirtyState( "entryHighlights" );
	for ( var key in entryHighlights ) {
		var st = key.split( ":" );
		var s = st[0];
		var t = st[1];
		var isHighlighted = ( key === thisEntryHighlight );
		if ( hashEntries.hasOwnProperty(key) ) {
			var entry = hashEntries[key];
			if ( isHighlighted !== entry.isHighlighted ) {
				entry.isHighlighted = isHighlighted;
				this.setDirty( "allEntries", entry.key, "isHighlighted" );
				this.__setDirtyModel( "allEntries", "isHighlighted" );
			}
		}
		if ( hashRowCrossRefs.hasOwnProperty(key) ) {
			var crossRef = hashRowCrossRefs[key];
			if ( isHighlighted !== crossRef.isHighlighted ) {
				crossRef.isHighlighted = isHighlighted;
				this.setDirty( "allRowCrossRefs", crossRef.key, "isHighlighted" );
				this.__setDirtyModel( "allRowCrossRefs", "isHighlighted" );
			}
		}
		if ( hashColumnCrossRefs.hasOwnProperty(key) ) {
			var crossRef = allColumnCrossRefs[key];
			if ( isHighlighted !== crossRef.isHighlighted ) {
				crossRef.isHighlighted = isHighlighted;
				this.setDirty( "allColumnCrossRefs", crossRef.key, "isHighlighted" );
				this.__setDirtyModel( "allColumnCrossRefs", "isHighlighted" );
			}
		}
	}
	for ( var s = 0; s < allRowElements.length; s++ ) {
		var element = allRowElements[s];
		var isHighlighted = ( s === thisRowHighlight );
		if ( isHighlighted !== element.isHighlighted ) {
			element.isHighlighted = isHighlighted;
			this.setDirty( "allRowElements", element.key, "isHighlighted" );
			this.__setDirtyModel( "allRowElements", "isHighlighted" );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		var isHighlighted = ( t === thisColumnHighlight );
		if ( isHighlighted !== element.isHighlighted ) {
			element.isHighlighted = isHighlighted;
			this.setDirty( "allColumnElements", element.key, "isHighlighted" );
			this.__setDirtyModel( "allColumnElements", "isHighlighted" );
		}
	}
};

MatrixModel.prototype.__onNoHighlights_exhaustiveLoops = function() {
	var allEntries = this.get( "allEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );
	var allRowCrossRefs = this.get( "allRowCrossRefs" );
	var allColumnCrossRefs = this.get( "allColumnCrossRefs" );

	var highlightSelectionIndex = undefined;
	if ( highlightSelectionIndex !== this.get( "highlightSelectionIndex" ) ) {
		this.set( "highlightSelectionIndex", highlightSelectionIndex );
		this.setDirty( "highlightSelectionIndex" );
	}
	
	for ( var n = 0; n < allEntries.length; n++ ) {
		var entry = allEntries[n];
		var isHighlighted = false;
		if ( isHighlighted !== entry.isHighlighted ) {
			entry.isHighlighted = isHighlighted;
			this.setDirty( "allEntries", entry.key, "isHighlighted" );
			this.__setDirtyModel( "allEntries", "isHighlighted" );
		}
	}
	for ( var s = 0; s < allRowElements.length; s++ ) {
		var element = allRowElements[s];
		var isHighlighted = false;
		if ( isHighlighted !== element.isHighlighted ) {
			element.isHighlighted = isHighlighted;
			this.setDirty( "allRowElements", element.key, "isHighlighted" );
			this.__setDirtyModel( "allRowElements", "isHighlighted" );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		var isHighlighted = false;
		if ( isHighlighted !== element.isHighlighted ) {
			element.isHighlighted = isHighlighted;
			this.setDirty( "allColumnElements", element.key, "isHighlighted" );
			this.__setDirtyModel( "allColumnElements", "isHighlighted" );
		}
	}
	for ( var st = 0; st < allRowCrossRefs.length; st++ ) {
		var crossRef = allRowCrossRefs[st];
		var isHighlighted = false;
		if ( isHighlighted !== crossRef.isHighlighted ) {
			crossRef.isHighlighted = isHighlighted;
			this.setDirty( "allRowCrossRefs", crossRef.key, "isHighlighted" );
			this.__setDirtyModel( "allRowCrossRefs", "isHighlighted" );
		}
	}
	for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
		var crossRef = allColumnCrossRefs[ts];
		var isHighlighted = false;
		if ( isHighlighted !== crossRef.isHighlighted ) {
			crossRef.isHighlighted = isHighlighted;
			this.setDirty( "allColumnCrossRefs", crossRef.key, "isHighlighted" );
			this.__setDirtyModel( "allColumnCrossRefs", "isHighlighted" );
		}
	}
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.__updateExpansions = function() {
	if ( this.__isDirtyState( "columnExpansions" ) )
	{
		var columnExpansions = this.state.get( "columnExpansions" );
		var thisColumnExpansion = _.keys( columnExpansions ).map( function(d) { return parseInt(d) } )[0];	// Take only the first highlight
		if ( thisColumnExpansion !== undefined )
			this.__onColumnExpansions_exhaustiveLoops( thisColumnExpansion );
		else
			this.__onNoExpansions_exhaustiveLoops();
	}
};

MatrixModel.prototype.__onColumnExpansions_exhaustiveLoops = function( thisColumnExpansion ) {
	var allEntries = this.get( "allEntries" );
	var allColumnElements = this.get( "allColumnElements" );
	var allColumnCrossRefs = this.get( "allColumnCrossRefs" );
	for ( var n = 0; n < allEntries.length; n++ ) {
		var entry = allEntries[n];
		var isExpanded = ( entry.columnIndex === thisColumnExpansion );
		if ( isExpanded !== entry.isExpanded ) {
			entry.isExpanded = isExpanded;
			this.setDirty( "allEntries", entry.key, "isExpanded" );
			this.__setDirtyModel( "allEntries", "isExpanded" );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		var isExpanded = ( t === thisColumnExpansion );
		if ( isExpanded !== element.isExpanded ) {
			element.isExpanded = isExpanded;
			this.setDirty( "allColumnElements", element.key, "isExpanded" );
			this.__setDirtyModel( "allColumnElements", "isExpanded" );
		}
	}
	for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
		var crossRef = allColumnCrossRefs[ts];
		var isExpanded = ( crossRef.columnIndex === thisColumnExpansion );
		if ( isExpanded !== crossRef.isExpanded ) {
			crossRef.isExpanded = isExpanded;
			this.setDirty( "allColumnCrossRefs", crossRef.key, "isExpanded" );
			this.__setDirtyModel( "allColumnCrossRefs", "isExpanded" );
		}
	}
};

MatrixModel.prototype.__onNoExpansions_exhaustiveLoops = function() {
	var allEntries = this.get( "allEntries" );
	var allColumnElements = this.get( "allColumnElements" );
	var allColumnCrossRefs = this.get( "allColumnCrossRefs" );
	for ( var n = 0; n < allEntries.length; n++ ) {
		var entry = allEntries[n];
		var isExpanded = false;
		if ( isExpanded !== entry.isExpanded ) {
			entry.isExpanded = isExpanded;
			this.setDirty( "allEntries", entry.key, "isExpanded" );
			this.__setDirtyModel( "allEntries", "isExpanded" );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		var isExpanded = false;
		if ( isExpanded !== element.isExpanded ) {
			element.isExpanded = isExpanded;
			this.setDirty( "allColumnElements", element.key, "isExpanded" );
			this.__setDirtyModel( "allColumnElements", "isExpanded" );
		}
	}
	for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
		var crossRef = allColumnCrossRefs[ts];
		var isExpanded = false;
		if ( isExpanded !== crossRef.isExpanded ) {
			crossRef.isExpanded = isExpanded;
			this.setDirty( "allColumnCrossRefs", crossRef.key, "isExpanded" );
			this.__setDirtyModel( "allColumnCrossRefs", "isExpanded" );
		}
	}
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.__updateInclusionsAndExclusions = function() {
	if ( this.__isDirtyState( "rowInExclusions" ) ) {
		var rowInExclusions = this.state.get( "rowInExclusions" );
		this.__onRowInExclusions_exhaustiveLoops( rowInExclusions );
	}
};

MatrixModel.prototype.__onRowInExclusions_exhaustiveLoops = function( rowInExclusions ) {
	var allEntries = this.get( "allEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allRowCrossRefs = this.get( "allRowCrossRefs" );

	for ( var n = 0; n < allEntries.length; n++ ) {
		var entry = allEntries[n];
		var s = entry.rowIndex;
		var isIncluded = ( rowInExclusions[s] === true );
		var isExcluded = ( rowInExclusions[s] === false );
		if ( isIncluded !== entry.isIncluded || isExcluded !== entry.isExcluded ) {
			entry.isIncluded = isIncluded;
			entry.isExcluded = isExcluded;
			this.setDirty( "allEntries", entry.key, [ "isIncluded", "isExcluded" ] );
			this.__setDirtyModel( "allEntries", [ "isIncluded", "isExcluded" ] );
		}
	}
	for ( var s = 0; s < allRowElements.length; s++ ) {
		var element = allRowElements[s];
		var isIncluded = ( rowInExclusions[s] === true );
		var isExcluded = ( rowInExclusions[s] === false );
		if ( isIncluded !== element.isIncluded || isExcluded !== element.isExcluded ) {
			element.isIncluded = isIncluded;
			element.isExcluded = isExcluded;
			this.setDirty( "allRowElements", element.key, [ "isIncluded", "isExcluded" ] );
			this.__setDirtyModel( "allRowElements", [ "isIncluded", "isExcluded" ] );
		}
	}
	for ( var ts = 0; ts < allRowCrossRefs.length; ts++ ) {
		var crossRef = allRowCrossRefs[ts];
		var s = crossRef.rowIndex;
		var isIncluded = ( rowInExclusions[s] === true );
		var isExcluded = ( rowInExclusions[s] === false );
		if ( isIncluded !== crossRef.isIncluded || isExcluded !== crossRef.isExcluded ) {
			crossRef.isIncluded = isIncluded;
			crossRef.isExcluded = isExcluded;
			this.setDirty( "allRowCrossRefs", crossRef.key, [ "isIncluded", "isExcluded" ] );
			this.__setDirtyModel( "allRowCrossRefs", [ "isIncluded", "isExcluded" ] );
		}
	}
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.__updatePromotionsAndDemotions = function() {
	if ( this.__isDirtyState( "entryProDemotions" ) ) {
		var entryProDemotions = this.state.get( "entryProDemotions" );
		this.__onEntryProDemotions_shortcutLoops( entryProDemotions );
	}
};

MatrixModel.prototype.__onEntryProDemotions_shortcutLoops = function( entryProDemotions ) {
	var allEntries = this.get( "allEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );

	var rowNumPromoted = this.__zeros( allRowElements.length );
	var rowNumDemoted = this.__zeros( allRowElements.length );
	var columnNumPromoted = this.__zeros( allColumnElements.length );
	var columnNumDemoted = this.__zeros( allColumnElements.length );

	for ( var n = 0; n < allEntries.length; n++ ) {
		var entry = allEntries[n];
		var key = entry.key;
		var s = entry.rowIndex;
		var t = entry.columnIndex;
		var isPromoted = ( entryProDemotions[key] === true );
		var isDemoted = ( entryProDemotions[key] === false );
		if ( isPromoted !== entry.isPromoted || isDemoted !== entry.isDemoted ) {
			entry.isPromoted = isPromoted;
			entry.isDemoted = isDemoted;
			this.setDirty( "allEntries", entry.key, [ "isPromoted", "isDemoted" ] );
			this.__setDirtyModel( "allEntries", [ "isPromoted", "isDemoted" ] );
		}
		if ( entryProDemotions[key] === true ) {
			rowNumPromoted[s] ++;
			columnNumPromoted[t] ++;
		}
		if ( entryProDemotions[key] === false ) {
			rowNumDemoted[s] ++;
			columnNumDemoted[t] ++;
		}
	}
	for ( var s = 0; s < allRowElements.length; s++ ) {
		var element = allRowElements[s];
		if ( rowNumPromoted[s] !== element.numPromoted || rowNumDemoted[s] !== element.numDemoted ) {
			element.numPromoted = rowNumPromoted[s];
			element.numDemoted = rowNumDemoted[s];
			this.setDirty( "allRowElements", s, [ "numPromoted", "numDemoted" ] );
			this.__setDirtyModel( "allRowElements", [ "numPromoted", "numDemoted" ] );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		if ( columnNumPromoted[t] !== element.numPromoted || columnNumDemoted[t] !== element.numDemoted ) {
			element.numPromoted = columnNumPromoted[t];
			element.numDemoted = columnNumDemoted[t];
			this.setDirty( "allColumnElements", t, [ "numPromoted", "numDemoted" ] );
			this.__setDirtyModel( "allColumnElements", [ "numPromoted", "numDemoted" ] );
		}
	}
};

MatrixModel.prototype.__onEntryProDemotions_shortcutLoops = function( entryProDemotions ) {
	var hashEntries = this.get( "hashEntries" );
	var allRowElements = this.get( "allRowElements" );
	var allColumnElements = this.get( "allColumnElements" );
	var entryIndexes = this.__entryIndexes( this.__getDirtyState( "entryProDemotions" ) );

	var rowNumPromoted = this.__zeros( allRowElements.length );
	var rowNumDemoted = this.__zeros( allRowElements.length );
	var columnNumPromoted = this.__zeros( allColumnElements.length );
	var columnNumDemoted = this.__zeros( allColumnElements.length );
	for ( var i in entryIndexes ) {
		var key = entryIndexes[i];
		if ( hashEntries.hasOwnProperty(key) ) {
			var entry = hashEntries[key];
			var s = entry.rowIndex;
			var t = entry.columnIndex;
			var isPromoted = ( entryProDemotions[key] === true );
			var isDemoted = ( entryProDemotions[key] === false );
			if ( isPromoted !== entry.isPromoted || isDemoted !== entry.isDemoted ) {
				if ( ! entry.isPromoted && isPromoted ) {
					rowNumPromoted[s] ++;
					columnNumPromoted[t] ++;
				}
				if ( entry.isPromoted && ! isPromoted ) {
					rowNumPromoted[s] --;
					columnNumPromoted[t] --;
				}
				if ( ! entry.isDemoted && isDemoted ) {
					rowNumDemoted[s] ++;
					columnNumDemoted[t] ++;
				}
				if ( entry.isDemoted && ! isDemoted ) {
					rowNumDemoted[s] --;
					columnNumDemoted[t] --;
				}
				entry.isPromoted = isPromoted;
				entry.isDemoted = isDemoted;
				this.setDirty( "allEntries", entry.key, [ "isPromoted", "isDemoted" ] );
				this.__setDirtyModel( "allEntries", [ "isPromoted", "isDemoted" ] );
			}
		}
	}
	for ( var s = 0; s < allRowElements.length; s++ ) {
		var element = allRowElements[s];
		if ( rowNumPromoted[s] !== 0 || rowNumDemoted[s] !== 0 ) {
			element.numPromoted = rowNumPromoted[s] + ( element.numPromoted || 0 );
			element.numDemoted = rowNumDemoted[s] + ( element.numDemoted || 0 );
			this.setDirty( "allRowElements", s, [ "numPromoted", "numDemoted" ] );
			this.__setDirtyModel( "allRowElements", [ "numPromoted", "numDemoted" ] );
		}
	}
	for ( var t = 0; t < allColumnElements.length; t++ ) {
		var element = allColumnElements[t];
		if ( columnNumPromoted[t] !== 0 || columnNumDemoted[t] !== 0 ) {
			element.numPromoted = columnNumPromoted[t] + ( element.numPromoted || 0 );
			element.numDemoted = columnNumDemoted[t] + ( element.numDemoted || 0 );
			this.setDirty( "allColumnElements", t, [ "numPromoted", "numDemoted" ] );
			this.__setDirtyModel( "allColumnElements", [ "numPromoted", "numDemoted" ] );
		}
	}
};

MatrixModel.prototype.__zeros = function( N ) {
	var array = new Array( N );
	for ( var n = 0; n < N; n++ )
		array[n] = 0;
	return array;
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.__updateTexts = function() {
	if ( this.__isDirtyState( "rowLabels" ) ) {
		var allRowElements = this.get( "allRowElements" );
		var rowLabels = this.state.get( "rowLabels" );
		for ( var s = 0; s < allRowElements.length; s++ ) {
			var element = allRowElements[s];
			var text = rowLabels[s];
			if ( text !== element.text ) {
				element.text = text;
				this.setDirty( "allRowElements", element.key, "text" );
				this.__setDirtyModel( "allRowElements", "text" );
			}
		}
	}	
	if ( this.__isDirtyState( "columnLabels" ) ) {
		var allColumnElements = this.get( "allColumnElements" );
		var columnLabels = this.state.get( "columnLabels" );
		for ( var t = 0; t < allColumnElements.length; t++ ) {
			var element = allColumnElements[t];
			var text = columnLabels[t];
			if ( text !== element.text ) {
				element.text = text;
				this.setDirty( "allColumnElements", element.key, "text" );
				this.__setDirtyModel( "allColumnElements", "text" );
			}
		}
	}
	if ( this.__isDirtyModel( "allColumnElements", [ "numVisibles", "isSelected", "numOrdered", "numPromoted" ] ) ) {
		var allColumnElements = this.get( "allColumnElements" );
		var columnNumVisibleRows = this.state.get( "columnNumVisibleRows" );
		for ( var t = 0; t < allColumnElements.length; t++ ) {
			var element = allColumnElements[t];
			var icons = [];

//			if ( element.numVisibles > 0 && element.numOrdered > 0 )
//				icons.push( "priority" );
			if ( element.numVisibles > 0 )
				icons.push( "visibility" );
			if ( element.numOrdered > 0 )
				icons.push( "ordering" );
			if ( element.numPromoted > 0 )
				icons.push( "promotions" );
			if ( element.isSelected )
				icons.push( "selection" )
			icons = icons.join( ";" );
			if ( icons !== element.icons ) {
				element.icons = icons;
				this.setDirty( "allColumnElements", element.key, "icons" );
				this.__setDirtyModel( "allColumnElements", "icons" );
			}
		}
	}
};
