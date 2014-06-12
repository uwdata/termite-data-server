MatrixModel.prototype.__updateEntryValues = function() {
	if ( this.__isDirtyState( "normalization" ) || 
		 this.__isDirtyModel( [ "maxJointProbability", "rowRescaleMultiplier", "columnRescaleMultiplier" ] ) ||
		 this.__isDirtyModel( "allEntries", [ "relValue", "rowRelValue", "columnRelValue" ] ) )
	{
		var allEntries = this.get( "allEntries" );
		var normalization = this.state.get( "normalization" );
		var maxJointProbability = this.get( "maxJointProbability" );
		var rowRescaleMultiplier = this.get( "rowRescaleMultiplier" );
		var columnRescaleMultiplier = this.get( "columnRescaleMultiplier" );
		var maxValue = undefined;
		
		if ( normalization === "none" ) {
			for ( var n = 0; n < allEntries.length; n++ ) {
				var entry = allEntries[n];
				var value = entry.relValue;
				if ( value !== entry.value ) {
					entry.value = value;
					this.setDirty( "allEntries", entry.key, "value" );
				}
			}
			maxValue = maxJointProbability;
		}
		else if ( normalization === "row" ) {
			for ( var n = 0; n < allEntries.length; n++ ) {
				var entry = allEntries[n];
				var value = entry.rowRelValue;
				if ( value !== entry.value ) {
					entry.value = value;
					this.setDirty( "allEntries", entry.key, "value" );
				}
			}
			maxValue = maxJointProbability * rowRescaleMultiplier;
		}
		else if ( normalization === "column" ) {
			for ( var n = 0; n < allEntries.length; n++ ) {
				var entry = allEntries[n];
				var value = entry.columnRelValue;
				if ( value !== entry.value ) {
					entry.value = value;
					this.setDirty( "allEntries", entry.key, "value" );
				}
			}
			maxValue = maxJointProbability * columnRescaleMultiplier;
		}
		if ( maxValue !== this.get( "maxValue" ) ) {
			this.set( "maxValue", maxValue )
			this.setDirty( "maxValue" );
		}
		this.__setDirtyModel( "allEntries", "value" );
	}
};

MatrixModel.prototype.__updateRowColumnValues = function() {
	if ( this.__isDirtyState( "normalization" ) ||
		 this.__isDirtyModel( "maxRowMarginalProbability" ) ||
		 this.__isDirtyModel( "allRowElements", "relValue" ) )
	{
		var normalization = this.state.get( "normalization" );
		var allRowElements = this.get( "allRowElements" );
		var maxRowMarginalProbability = this.get( "maxRowMarginalProbability" );
		var maxRowValue = undefined;
		if ( normalization === "row" ) {
			for ( var s = 0; s < allRowElements.length; s++ ) {
				var element = allRowElements[s];
				var value = 1.0;
				if ( value !== element.value ) {
					element.value = value;
					this.setDirty( "allRowElements", element.key, "value" );
				}
			}
			maxRowValue = 1.0;
		}
		else {
			for ( var s = 0; s < allRowElements.length; s++ ) {
				var element = allRowElements[s];
				var value = element.relValue;
				if ( value !== element.value ) {
					element.value = value;
					this.setDirty( "allRowElements", element.key, "value" );
				}
			}
			maxRowValue = maxRowMarginalProbability;
		}
		if ( maxRowValue !== this.get( "maxRowValue" ) ) {
			this.set( "maxRowValue", maxRowValue );
			this.setDirty( "maxRowValue" );
		}
		this.__setDirtyModel( "allRowElements", "value" );
	}
	
	if ( this.__isDirtyState( "normalization" ) ||
		 this.__isDirtyModel( "maxColumnMarginalProbability" ) ||
		 this.__isDirtyModel( "allColumnElements", "relValue" ) )
	{
		var normalization = this.state.get( "normalization" );
		var allColumnElements = this.get( "allColumnElements" );
		var maxColumnMarginalProbability = this.get( "maxColumnMarginalProbability" );
		var maxColumnValue = undefined;
		if ( normalization == "column" ) {
			for ( var t = 0; t < allColumnElements.length; t++ ) {
				var element = allColumnElements[t];
				var value = 1.0;
				if ( value !== element.value ) {
					element.value = value;
					this.setDirty( "allColumnElements", element.key, "value" );
				}
			}
			maxColumnValue = 1.0;
		}
		else {
			for ( var t = 0; t < allColumnElements.length; t++ ) {
				var element = allColumnElements[t];
				var value = element.relValue;
				if ( value !== element.value ) {
					element.value = value;
					this.setDirty( "allColumnElements", element.key, "value" );
				}
			}
			maxColumnValue = maxColumnMarginalProbability;
		}
		if ( maxColumnValue !== this.get( "maxColumnValue" ) ) {
			this.set( "maxColumnValue", maxColumnValue );
			this.setDirty( "maxColumnValue" );
		}
		this.__setDirtyModel( "allColumnElements", "value" );
	}
};

MatrixModel.prototype.__updateCrossRefValues = function() {
	if ( this.__isDirtyState( "normalization" ) ||
		 this.__isDirtyState( "allEntries", [ "relValue", "rowRelValue" ] ) ||
		 this.__isDirtyModel( "allRowCrossRefs", [ "isSelected", "isHighlighted", "isVisible" ] ) )
	{
		var normalization = this.state.get( "normalization" );
		var allRowCrossRefs = this.get( "allRowCrossRefs" );
		if ( normalization === "row" ) {
			for ( var st = 0; st < allRowCrossRefs.length; st++ ) {
				var crossRef = allRowCrossRefs[st];
				var value = ( ( crossRef.isSelected || crossRef.isHighlighted ) && crossRef.isVisible ) ? crossRef.entry.rowRelValue : 0;
				if ( value !== crossRef.value ) {
					crossRef.value = value;
					this.setDirty( "allRowCrossRefs", crossRef.key, "value" );
				}
			}
		}
		else {
			for ( var st = 0; st < allRowCrossRefs.length; st++ ) {
				var crossRef = allRowCrossRefs[st];
				var value = ( ( crossRef.isSelected || crossRef.isHighlighted ) && crossRef.isVisible ) ? crossRef.entry.relValue : 0;
				if ( value !== crossRef.value ) {
					crossRef.value = value;
					this.setDirty( "allRowCrossRefs", crossRef.key, "value" );
				}
			}
		}
		this.__setDirtyModel( "allRowCrossRefs", "value" );
	}
	
	if ( this.__isDirtyState( "normalization" ) ||
		 this.__isDirtyState( "allEntries", [ "relValue", "columnRelValue" ] ) ||
		 this.__isDirtyModel( "allColumnCrossRefs", [ "isSelected", "isHighlighted", "isVisible" ] ) )
	{
		var normalization = this.state.get( "normalization" );
		var allColumnCrossRefs = this.get( "allColumnCrossRefs" );
		if ( normalization === "column" ) {
			for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
				var crossRef = allColumnCrossRefs[ts];
				var value = ( ( crossRef.isSelected || crossRef.isHighlighted ) && crossRef.isVisible ) ? crossRef.entry.columnRelValue : 0;
				if ( value !== crossRef.value ) {
					crossRef.value = value;
					this.setDirty( "allColumnCrossRefs", crossRef.key, "value" );
				}
			}
		}
		else {
			for ( var ts = 0; ts < allColumnCrossRefs.length; ts++ ) {
				var crossRef = allColumnCrossRefs[ts];
				var value = ( ( crossRef.isSelected || crossRef.isHighlighted ) && crossRef.isVisible ) ? crossRef.entry.relValue : 0;
				if ( value !== crossRef.value ) {
					crossRef.value = value;
					this.setDirty( "allColumnCrossRefs", crossRef.key, "value" );
				}
			}
		}
		this.__setDirtyModel( "allColumnCrossRefs", "value" );
	}
};

//--------------------------------------------------------------------------------------------------

MatrixModel.prototype.__updateCrossRefPositionsAndSizes = function() {
	if ( this.__isDirtyState( "columnUserDefinedOrdering" ) || this.__isDirtyModel( "allRowCrossRefs", "value" ) )
	{
		var columnUserDefinedOrdering = this.state.get( "columnUserDefinedOrdering" );
		var allRowElements = this.get( "allRowElements" );
		for ( var s = 0; s < allRowElements.length; s++ ) {
			var element = allRowElements[s];
			var tally = 0.0;
			for ( var i = 0; i < columnUserDefinedOrdering.length; i++ ) {
				var t = columnUserDefinedOrdering[i];
				if ( element.crossRefs.hasOwnProperty(t) ) {
					var crossRef = element.crossRefs[t];
					var startValue = tally;
					tally += crossRef.value;
					var endValue = tally;
					if ( startValue !== crossRef.startValue || endValue !== crossRef.endValue ) {
						crossRef.startValue = startValue;
						crossRef.endValue = endValue;
						this.setDirty( "allRowCrossRefs", crossRef.key, [ "startValue", "endValue" ] );
					}
				}
			}
		}
		this.__setDirtyModel( "allRowCrossRefs", [ "startValue", "endValue" ] );
	}
	
	if ( this.__isDirtyState( "rowUserDefinedOrdering" ) || this.__isDirtyModel( "allColumnCrossRefs", "value" ) )
	{
		var rowUserDefinedOrdering = this.state.get( "rowUserDefinedOrdering" );
		var allColumnElements = this.get( "allColumnElements" );
		
		for ( var t = 0; t < allColumnElements.length; t++ ) {
			var element = allColumnElements[t];
			var tally = 0.0;
			for ( var i = 0; i < rowUserDefinedOrdering.length; i++ ) {
				var s = rowUserDefinedOrdering[i];
				if ( element.crossRefs.hasOwnProperty(s) ) {
					var crossRef = element.crossRefs[s];
					var startValue = tally;
					tally += crossRef.value;
					var endValue = tally;
					if ( startValue !== crossRef.startValue || endValue !== crossRef.endValue ) {
						crossRef.startValue = startValue;
						crossRef.endValue = endValue;
						this.setDirty( "allColumnCrossRefs", crossRef.key, [ "startValue", "endValue" ] );
					}
				}
			}
		}
		
		this.__setDirtyModel( "allColumnCrossRefs", [ "startValue", "endValue" ] );
	}
};

