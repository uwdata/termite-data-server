MatrixModel.prototype.__updateAnnotationControls = function() {
	if ( this.__getDirtyState() === true ) {
		this.__setDirtyModelAndValue( "hashAnnotationControls", {} );
		this.__setDirtyModelAndValue( "allAnnotationControls", [] );
	}
	if ( this.__isDirtyState( "columnExpansions" ) || this.__isDirtyModel( "allRowElements", "isVisible" ) ) {
		var hashAnnotationControls = this.get( "hashAnnotationControls" ) || {};
		var allAnnotationControls = this.get( "allAnnotationControls" ) || [];
		var ss = [];
		var tt = [];
		var allRowElements = this.get( "allRowElements" );
		var columnExpansions = this.state.get( "columnExpansions" );
		for ( var s = 0; s < allRowElements.length; s++ )
			if ( allRowElements[s].isVisible )
				ss.push(s);
		for ( var t in columnExpansions )
			tt.push( parseInt(t) );

		// Create controls
		var newAnnotationControls = [];
		for ( var i = 0; i < ss.length; i++ ) {
			var s = ss[i];
			for ( var j = 0; j < tt.length; j++ ) {
				var t = tt[j];
				var key = s + ":" + t;
				if ( ! hashAnnotationControls.hasOwnProperty( key ) ) {
					var control = { 
						"rowIndex" : s, 
						"columnIndex" : t, 
						"key" : key,
						"dataType" : "promoteDemote"
					};
					hashAnnotationControls[ key ] = control;
					newAnnotationControls.push( control );
				}
			}
		}
		if ( newAnnotationControls.length > 0 ) {
			this.__setDirtyModelAndValue( "hashAnnotationControls", hashAnnotationControls );
			this.__setDirtyModelAndValue( "allAnnotationControls", allAnnotationControls.concat( newAnnotationControls ) );
		}
	}
	
	var allAnnotationControls = this.get( "allAnnotationControls" ) || [];

	if ( this.__getDirtyModel( "allAnnotationControls" ) === true || this.__isDirtyModel( "allColumnElements", "columnPosition" ) ) {
		var allColumnElements = this.get( "allColumnElements" );
		for ( var n = 0; n < allAnnotationControls.length; n++ ) {
			var control = allAnnotationControls[ n ];
			var columnPosition = allColumnElements[ control.columnIndex ].columnPosition;
			if ( columnPosition !== control.columnPosition ) {
				control.columnPosition = columnPosition;
				this.setDirty( "allAnnotationControls", control.key, "columnPosition" );
				this.__setDirtyModel( "allAnnotationControls", "columnPosition" );
			}
		}
	}

	if ( this.__getDirtyModel( "allAnnotationControls" ) === true || this.__isDirtyModel( "allRowElements", "rowPosition" ) ) {
		var allRowElements = this.get( "allRowElements" );
		for ( var n = 0; n < allAnnotationControls.length; n++ ) {
			var control = allAnnotationControls[ n ];
			var rowPosition = allRowElements[ control.rowIndex ].rowPosition;
			if ( rowPosition !== control.rowPosition ) {
				control.rowPosition = rowPosition;
				this.setDirty( "allAnnotationControls", control.key, "rowPosition" );
				this.__setDirtyModel( "allAnnotationControls", "rowPosition" );
			}
		}
	}

	if ( this.__getDirtyModel( "allAnnotationControls" ) === true || this.__isDirtyModel( "allRowElements", "text" ) ) {
		var allRowElements = this.get( "allRowElements" );
		for ( var n = 0; n < allAnnotationControls.length; n++ ) {
			var control = allAnnotationControls[ n ];
			var text = allRowElements[ control.rowIndex ].text;
			if ( text !== control.text ) {
				control.text = text;
				this.setDirty( "allAnnotationControls", control.key, "text" );
				this.__setDirtyModel( "allAnnotationControls", "text" );
			}
		}
	}
	
	if ( this.__getDirtyModel( "allAnnotationControls" ) === true || this.__isDirtyModel( "allColumnElements", [ "isSelected", "selectionIndex" ] ) ) {
		var allColumnElements = this.get( "allColumnElements" );
		for ( var n = 0; n < allAnnotationControls.length; n++ ) {
			var control = allAnnotationControls[ n ];
			var element = allColumnElements[ control.columnIndex ];
			var isSelected = element.isSelected;
			if ( isSelected !== control.isSelected ) {
				control.isSelected = isSelected;
				if ( control.isSelected )
					control.selectionIndex = element.selectionIndex;
				else
					delete control.selectionIndex;
				this.setDirty( "allAnnotationControls", control.key, [ "isSelected", "selectionIndex" ] );
				this.__setDirtyModel( "allAnnotationControls", [ "isSelected", "selectionIndex" ] );
			}
		}
	}
	
	if ( this.__getDirtyModel( "allAnnotationControls" ) === true || this.__isDirtyState( "entryProDemotions" ) ) {
		var entryProDemotions = this.state.get( "entryProDemotions" );
		for ( var n = 0; n < allAnnotationControls.length; n++ ) {
			var control = allAnnotationControls[ n ];
			var key = control.key;
			var isPromoted = ( entryProDemotions[key] === true );
			var isDemoted = ( entryProDemotions[key] === false );
			if ( isPromoted !== control.isPromoted || isDemoted !== control.isDemoted ) {
				control.isPromoted = isPromoted;
				control.isDemoted = isDemoted;
				this.setDirty( "allAnnotationControls", control.key, [ "isPromted", "isDemoted" ] );
				this.__setDirtyModel( "allAnnotationControls", [ "isPromoted", "isDemoted" ] );
			}
		}
	}

	var allRowElements = this.get( "allRowElements" );
	var columnExpansions = this.state.get( "columnExpansions" );
	for ( var n = 0; n < allAnnotationControls.length; n++ ) {
		var control = allAnnotationControls[ n ];
		var wasVisible = ( control.isVisible === true );
		var isVisible = ( allRowElements[ control.rowIndex ].isVisible && columnExpansions.hasOwnProperty( control.columnIndex ) );
		control.isEnter = ( !wasVisible && isVisible );
		control.isStay = ( wasVisible && isVisible );
		control.isExit = ( wasVisible && !isVisible );
		if ( isVisible !== control.isVisible ) {
			control.isVisible = isVisible;
			this.setDirty( "allAnnotationControls", control.key, "isVisible" );
			this.__setDirtyModel( "allAnnotationControls", [ "isEnter", "isStay", "isExit", "isVisible" ] );
		}
	}
};