MatrixModel.prototype.__updateSelectionGroups = function() {
	if ( this.__isDirtyState( "selectionCount" ) ) {
		var selectionCount = this.state.get( "selectionCount" );
		var hashSelectionGroups = this.get( "hashSelectionGroups" ) || {};
		var allSelectionGroups = this.get( "allSelectionGroups" ) || [];

		// Create controls
		var newSelectionGroups = [];
		for ( var selectionIndex = 0; selectionIndex < selectionCount; selectionIndex++ ) {
			if ( ! hashSelectionGroups.hasOwnProperty( selectionIndex ) ) {
				var selection = {
					"key" : selectionIndex,
					"selectionIndex" : selectionIndex,
					"dataType" : "selection"
				};
				hashSelectionGroups[ selectionIndex ] = selection;
				newSelectionGroups.push( selection );
			}
		}
		if ( newSelectionGroups.length > 0 ) {
			this.__setDirtyModelAndValue( "hashSelectionGroups", hashSelectionGroups );
			this.__setDirtyModelAndValue( "allSelectionGroups", allSelectionGroups.concat( newSelectionGroups ) );
		}
	}
	
	var allSelectionGroups = this.get( "allSelectionGroups" ) || [];

	if ( this.__getDirtyModel( "allSelectionGroups" ) === true || this.__isDirtyState( "selectionLabels" ) ) {
		var selectionLabels = this.state.get( "selectionLabels" );
		var selectionIndexes = this.__selectionIndexes( this.__getDirtyState( "selectionLabels" ) );
		for ( var i = 0; i < selectionIndexes.length; i++ ) {
			var selectionIndex = selectionIndexes[i];
			var selection = allSelectionGroups[ selectionIndex ];
			var text = selectionLabels[ selectionIndex ];
			if ( text !== selection.text ) {
				selection.text = text;
				this.setDirty( "allSelectionGroups", selectionIndex, "text" );
				this.__setDirtyModel( "allSelectionGroups", "text" );
			}
		}
	}
	if ( this.__getDirtyModel( "allSelectionGroups" ) === true || this.__isDirtyState( "selectionColors" ) ) {
		var selectionColors = this.state.get( "selectionColors" );
		var selectionIndexes = this.__selectionIndexes( this.__getDirtyState( "selectionColors" ) );
		for ( var i = 0; i < selectionIndexes.length; i++ ) {
			var selectionIndex = selectionIndexes[i];
			var selection = allSelectionGroups[ selectionIndex ];
			var color = selectionColors[ selectionIndex ];
			if ( color !== selection.color ) {
				selection.color = color;
				this.setDirty( "allSelectionGroups", selectionIndex, "color" );
				this.__setDirtyModel( "allSelectionGroups", "color" );
			}
		}
	}
	if ( this.__getDirtyModel( "allSelectionGroups" ) === true || this.__isDirtyState( "selectionBackgrounds" ) ) {
		var selectionBackgrounds = this.state.get( "selectionBackgrounds" );
		var selectionIndexes = this.__selectionIndexes( this.__getDirtyState( "selectionBackgrounds" ) );
		for ( var i = 0; i < selectionIndexes.length; i++ ) {
			var selectionIndex = selectionIndexes[i];
			var selection = allSelectionGroups[ selectionIndex ];
			var background = selectionBackgrounds[ selectionIndex ];
			if ( background !== selection.background ) {
				selection.background = background;
				this.setDirty( "allSelectionGroups", selectionIndex, "background" );
				this.__setDirtyModel( "allSelectionGroups", "background" );
			}
		}
	}
	if ( this.__getDirtyModel( "allSelectionGroups" ) === true || this.__isDirtyState( "columnSelections" ) ) {
		var columnSelections = this.state.get( "columnSelections" );
		var allColumnElements = this.get( "allColumnElements" );
		var selectionColumnIndexes = new Array( allSelectionGroups.length );
		for ( var selectionIndex = 0; selectionIndex < selectionColumnIndexes.length; selectionIndex++ )
			selectionColumnIndexes[ selectionIndex ] = {};
		for ( var t in columnSelections ) {
			var t = parseInt(t);
			var element = allColumnElements[ t ];
			var selectionIndex = columnSelections[ t ];
			selectionColumnIndexes[ selectionIndex ][ t ] = element;
		}
		for ( var selectionIndex = 0; selectionIndex < allSelectionGroups.length; selectionIndex++ ) {
			var selection = allSelectionGroups[ selectionIndex ];
			var a = selectionColumnIndexes[ selectionIndex ];
			var b = selection.columnIndexes;
			var aKeys = _.keys( a );
			var bKeys = ( b ? _.keys( b ) : [] );
			if ( b === undefined || _.difference( aKeys, bKeys ).length > 0 || _.difference( bKeys, aKeys ).length > 0 ) {
				selection.columnIndexes = selectionColumnIndexes[ selectionIndex ];
				this.setDirty( "allSelectionGroups", selectionIndex, "columnIndexes" );
				this.__setDirtyModel( "allSelectionGroups", "columnIndexes" );
			}
		}
	}
};

