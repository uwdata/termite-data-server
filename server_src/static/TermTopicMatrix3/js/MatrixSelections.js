var MatrixSelections = MatrixInteractions.extend({
	el : "div.MatrixSelections"
});

MatrixSelections.prototype.initialize = function( options ) {
	MatrixInteractions.prototype.initialize.call( this, options );
	this.model = options.model;
	this.state = this.model.state;
	
	this.$el.addClass( "MatrixView" );
	this.__container = d3.select( this.el ).append( "div" ).attr( "class", "container" );

	this.__selectionPanel = this.__container.append( "div" ).style( "position", "static" );
	this.listenTo( this.model, "dirty", this.__onModelEvents );
};

MatrixSelections.prototype.__isDirtyModel = function() {
	var keys = Array.prototype.slice.call( arguments );
	return this.__isDirty__( this.__currentModelEvents, keys, 0 );
};

MatrixSelections.prototype.__getDirtyModel = function() {
	var keys = Array.prototype.slice.call( arguments );
	return this.__getDirty__( this.__currentModelEvents, keys, 0 );
};

MatrixSelections.prototype.__onModelEvents = function( dirty ) {
	this.__currentModelEvents = dirty;
	
	if ( this.__isDirtyModel( "allSelectionGroups" ) ) {
		this.__renderSelectionGroups();
	}
	return;
};

MatrixSelections.prototype.__renderSelectionGroups = function() {
	var allSelectionGroups = this.model.get( "allSelectionGroups" );
	
	if ( this.__getDirtyModel( "allSelectionGroups" ) === true ) {
		this.__selectionPanel.call( containerRenderer.bind(this) );
		var selectionGroups = this.__selectionPanel.selectAll( "div.selectionGroup" ).data( allSelectionGroups )
		selectionGroups.enter().append( "div" ).attr( "class", "selectionGroup" ).call( enterRenderer.bind(this) );
		selectionGroups.exit().remove();
	}
	
	this.__selectionPanel.selectAll( "div.selectionGroup" ).call( updateRenderer.bind(this) )
		.transition().call( updateAnimations.bind(this) );
	
	function containerRenderer( e ) {
		e.style( "width", "120px" )
		 .style( "min-height", "100px" )
		 .style( "padding", "5px" )
	}
	function enterRenderer( e ) {
		e.style( "position", "static" )
		 .style( "display", "inline-block" )
		 .style( "width", "118px" )
		 .style( "min-height", "50px" )
		 .style( "margin-top", function(d,i) { return ( i === 0 ) ? null : "5px" } )
		 .style( "border-width", "1px" )
		 .style( "border-style", "solid" )
		 .style( "border-color", function(d) { return d.color } )
		 .style( "background", function(d) { return d.background } )
		 .call( this.mouseListeners.bind(this) )
		 .call( this.dragdropListeners.bind(this) )
		var selectionBox = e.append( "div" ).attr( "class", "selection" )
			.style( "width", "16px" )
			.style( "padding", "3px" )
			.style( "pointer-events", "auto" )
			.style( "cursor", "pointer" )
			.append( "i" )
				.attr( "class", this.CONST.ICONS.SELECTION )
			 	.style( "color", function(d) { return d.color } )
				.style( "font-size", this.CONST.FONT_SIZE_PT * 2 + "pt" )
		var titleBox = e.append( "input" ).attr( "class", "title" )
			.attr( "type", "text" )
			.style( "margin", "0 2px" )
			.style( "width", "90px" )
			.style( "border-width", "2px" )
			.style( "border-style", "dotted" )
		 	.style( "font-size", this.CONST.FONT_SIZE_PT + "pt" )
			.style( "cursor", "text" )
			.style( "pointer-events", "auto" )
			.on( "mouseover", function(d) { d3.select(d3.event.srcElement).style( "border-color", d.color ) }.bind(this) )
			.on( "mouseout", function(d) { d3.select(d3.event.srcElement).style( "border-color", d.background ) }.bind(this) )
			.on( "focus", function(d) { d3.select(d3.event.srcElement).style( "background", "#fff" ) }.bind(this) )
			.on( "blur", function(d) { d3.select(d3.event.srcElement).style( "background", d.background ) }.bind(this) )
			.on( "keydown", function() { d3.event.cancelBubble = true } )
			.on( "change", onChangeSelectionLabel.bind(this) )
		var visibilityBox = e.append( "div" ).attr( "class", "visibility" )
			.style( "width", "100px" )
			.style( "padding", "3px 5px 0 5px" )
		visibilityBox.append( "div" )
			.append( "i" )
				.attr( "class", this.CONST.ICONS.VISIBILITY )
				.style( "padding", "0 3px" )
			 	.style( "color", function(d) { return d.color } )
				.style( "font-size", this.CONST.FONT_SIZE_PT + "pt" )
		visibilityBox.append( "div" )
			.append( "input" )
			.attr( "type", "range" )
			.attr( "min", getSelectionMinVisibleRowQuantile.bind(this) )
			.attr( "max", getSelectionMaxVisibleRowQuantile.bind(this) )
			.attr( "value", getSelectionVisibleRowQuantile.bind(this) )
			.style( "width", "80px" )
			.style( "opacity", 0.3 )
			.style( "vertical-align", "-5px" )
			.style( "cursor", "pointer" )
			.style( "pointer-events", "auto" )
			.on( "mouseover", function() { d3.select(d3.event.srcElement).transition().style( "opacity", 1 ) } )
			.on( "mouseout", function() { d3.select(d3.event.srcElement).transition().style( "opacity", 0.3 ) } )
			.on( "change", onChangeSelectionVisibleRowQuantiles.bind(this) )
		var orderingBox = e.append( "div" ).attr( "class", "ordering" )
			.style( "width", "100px" )
			.style( "padding", "0 5px 3px 5px" )
		orderingBox.append( "div" )
			.append( "i" )
				.attr( "class", this.CONST.ICONS.ORDERING )
				.style( "padding", "0 3px" )
			 	.style( "color", function(d) { return d.color } )
				.style( "font-size", this.CONST.FONT_SIZE_PT + "pt" )
		orderingBox.append( "div" )
			.append( "input" )
			.attr( "type", "range" )
			.style( "width", "80px" )
			.style( "vertical-align", "-5px" )
			.style( "opacity", 0.1 )
//			.style( "cursor", "pointer" )
//			.style( "pointer-events", "auto" )
//			.on( "mouseover", function() { d3.select(d3.event.srcElement).transition().style( "opacity", 1 ) } )
//			.on( "mouseout", function() { d3.select(d3.event.srcElement).transition().style( "opacity", 0.3 ) } )
	}
	function updateRenderer( e ) {
		
	}
	function updateAnimations( e ) {
		var titleBox = e.select( "input.title" )
		 	.style( "color", function(d) { return d.color } )
			.style( "background", function(d) { return d.background } )
			.style( "border-color", function(d) { return d.background } )
			.attr( "value", function(d) { return d.text } )
	}
	function getSelectionMinVisibleRowQuantile( data ) {
		return this.state.CONST.MIN_VISIBLE_ROW_QUANTILES;
	}
	function getSelectionMaxVisibleRowQuantile( data ) {
		return this.state.CONST.MAX_VISIBLE_ROW_QUANTILES;
	}
	function getSelectionVisibleRowQuantile( data ) {
		var quantile = data.visibleRowQuantile;
		return quantile;
	}
	function onChangeSelectionVisibleRowQuantiles( data ) {
		this.state.selectionVisibleRowQuantiles( data.selectionIndex, parseInt( d3.event.srcElement.value ) );
		d3.event.srcElement.blur();
	}
	function onChangeSelectionLabel( data ) {
		this.state.selectionLabels( data.selectionIndex, d3.event.srcElement.value );
		d3.event.srcElement.blur();
	}
	

/*	this.__selectionColors = selectionInputs.append( "div" )
		.attr( "class", "selectionColor" )
		.style( "display", "inline-block" )
		.style( "vertical-align", "-5px" )
		.style( "width", "16px" )
		.style( "height", "16px" )
		.style( "margin", function(d) { return d.index === selectionIndex ? "0px" : "1px" } )
		.style( "border-width", "1px" )
		.style( "border-style", "solid" )
		.style( "border-width", function(d) { return d.index === selectionIndex ? "2px" : "1px" } )
		.style( "opacity", function(d) { return d.index === selectionIndex ? 1 : 0.5 } )
		.style( "border-color", function(d) { return d.color } )
		.style( "background", function(d) { return d.background } )
		.call( this.__mouseListeners.bind(this) )
		.call( this.__dragdropListeners.bind(this ))
	this.__selectionTexts = selectionInputs.append( "input" )
		.attr( "class", "selectionText" )
		.style( "display", "inline-block" )
		.style( "margin", "0 2px 3px 4px" )
		.style( "color", function(d) { return d.color } )
		.style( "border", function(d) { return d.isDisabled ? "1px solid #eee" : null } )
		.style( "background", function(d) { return d.isDisabled ? "#eee" : null } )
		.attr( "readonly", function(d) { return d.isDisabled ? "readonly" : null } )
		.attr( "value", function(d) { return d.label } )
		.on( "keydown", changeSelectionLabel );
};

	var changeSelectionLabel = function( data, index ) {
		if ( d3.event.keyCode == 13 ) {
			var label = d3.event.srcElement.value;
			this.state.selectionLabels( index, label );
			this.model.set( "ui:selectionIndex", index )
		}
	}.bind( this );
	var changeSelectionIndex = function( data, index ) {
		this.model.set( "ui:selectionIndex", data.index );
	}.bind( this );
*/
};

MatrixSelections.prototype.__onUpdateSelectionIndex = function() {
	var selectionIndex = this.model.get( "ui:selectionIndex" );
	this.__selectionColors
		.style( "margin", function(d) { return d.index === selectionIndex ? "0px" : "1px" } )
		.style( "border-width", function(d) { return d.index === selectionIndex ? "2px" : "1px" } )
		.style( "opacity", function(d) { return d.index === selectionIndex ? 1 : 0.5 } );
};


