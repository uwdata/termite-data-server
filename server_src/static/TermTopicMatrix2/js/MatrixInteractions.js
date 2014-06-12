var MatrixInteractions = CoreView.extend();

MatrixInteractions.prototype.CONST = {
	DEFAULT_COLOR : "#7f7f7f",
	DEFAULT_BACKGROUND : "#c7c7c7",
	HIGHLIGHT_COLOR : "#d62728",
	HIGHLIGHT_BACKGROUND : "#ff9896",
	
	FONT_SIZE_PT : 7.5,
	
	ANIMATION_DELAY : 275,
	ANIMATION_DURATION : 325,
	ANIMATION_EASE : "cubic-in-out",
	ANIMATION_STYLE_DURATION : 160,
	ANIMATION_STYLE_EASE : "linear",
	
	ICONS : {
		PROMOTIONS : "icon-ok-sign",
		NO_PROMOTIONS : "icon-ok",
		DEMOTIONS : "icon-remove-sign",
		NO_DEMOTIONS : "icon-remove",
		VISIBILITY : "icon-eye-open",
		ORDERING : "icon-sort", //"icon-sort-by-attributes-alt",
		SELECTION : "icon-tag",
		PRIORITY : "icon-signal" //"icon-sort-by-attributes-alt"
	}
};

MatrixInteractions.prototype.initialize = function( options ) {
	CoreView.prototype.initialize.call( this, options );
	this.model = options.model;
	this.state = this.model.state;
	this.__initInteractions();
};

MatrixInteractions.prototype.__registerMouseInteractions = function() {
	var mouseOverHighlights = function( isHighlighted, type, index, subindex ) {
		if ( isHighlighted )
			if ( type === "row" )
				this.state.rowHighlights( index );
			else if ( type === "column" )
				this.state.columnHighlights( index );
			else
				this.state.entryHighlights( index, subindex );
		else
			this.state.noHighlights();
	}.bind(this);
	this.__onMouseOverHighlights = _.debounce( mouseOverHighlights, 50 ).bind(this);
	var rowHighlightHandler = function(e) {
		this.__onMouseOverHighlights( true, "row", e.data.rowIndex )
	}.bind(this);
	var columnHighlightHandler = function(e) {
		this.__onMouseOverHighlights( true, "column", e.data.columnIndex )
	}.bind(this);
	var noHighlightHandler = function(e) {
		this.__onMouseOverHighlights( false );
	}.bind(this);
	
	var columnExpansionHandler = function(e) {
		var data = e.data;
		var selectionIndex = this.model.get( "ui:selectionIndex" );
		if ( data.isExpanded )
			this.state.noExpansions();
		else
			this.state.columnExpansions( data.columnIndex );
		this.model.set( "ui:columnIndex", data.columnIndex );
		d3.event.cancelBubble = true;
	}.bind(this);

	return [
		{ pattern : "fired:enter:row"          , handler : rowHighlightHandler    },
		{ pattern : "fired:exit:row"           , handler : noHighlightHandler     },
		{ pattern : "fired:enter:column"       , handler : columnHighlightHandler },
		{ pattern : "fired:exit:column"        , handler : noHighlightHandler     },
		{ pattern : "fired:enter:cell"         , handler : columnHighlightHandler },
		{ pattern : "fired:exit:cell"          , handler : noHighlightHandler     },
		{ pattern : "fired:enter:promoteDemote", handler : columnHighlightHandler },
		{ pattern : "fired:exit:promoteDemote" , handler : noHighlightHandler     },

		{ pattern : "fired:click:column"    , handler : columnExpansionHandler },
		{ pattern : "fired:click:cell"      , handler : columnExpansionHandler }
	];
};

MatrixInteractions.prototype.__registerReorderingDragAndDrops = function() {
	var onReorderDragStart = function(e) {
		this.model.set({
			"ui:dragColor" : e.data.isSelected ? this.model.get( "allSelectionGroups" )[ e.data.selectionIndex ].color: this.CONST.HIGHLIGHT_COLOR,
			"ui:dragBackground" : e.data.isSelected ? this.model.get( "allSelectionGroups" )[ e.data.selectionIndex ].background : this.CONST.HIGHLIGHT_BACKGROUND
		});
		d3.select( e.element )
			.style( "background", this.model.get( "ui:dragBackground" ) );
	}.bind(this);
	var onReorderDragEnd = function(e) {
		this.model.set({
			"ui:dragColor" : null,
			"ui:dragBackground" : null
		});
		d3.select( e.element )
			.style( "background", null );
	}.bind(this);
	var onReorderDragOver = function(e) {
		var isDropBefore = ( e.event.offsetY <= e.targetElement.offsetHeight / 2 );
		this.model.set({ "ui:isDropBefore" : isDropBefore });
		if ( isDropBefore )
			d3.select( e.targetElement )
				.style( "border-top", "1px solid " + this.model.get( "ui:dragColor" ) )
				.style( "border-bottom", null );
		else
			d3.select( e.targetElement )
				.style( "border-top", null )
				.style( "border-bottom", "1px solid " + this.model.get( "ui:dragColor" ) );
	}.bind(this);
	var onReorderDragLeave = function(e) {
		d3.select( e.targetElement )
			.style( "border-top", null )
			.style( "border-bottom", null );
	}.bind(this);
	var onRowToRowDragDrop = function(e) {
		onReorderDragLeave(e);
		if ( this.model.get( "ui:isDropBefore" ) )
			this.state.moveRowBefore( e.sourceData.rowIndex, e.targetData.rowIndex );
		else
			this.state.moveRowAfter( e.sourceData.rowIndex, e.targetData.rowIndex );
		this.state.noHighlights();
		this.model.set( "ui:rowIndex", e.sourceData.rowIndex );
	}.bind(this);
	var onColumnToColumnDragDrop = function(e) {
		onReorderDragLeave(e);
		if ( this.model.get( "ui:isDropBefore" ) )
			this.state.moveColumnBefore( e.sourceData.columnIndex, e.targetData.columnIndex );
		else
			this.state.moveColumnAfter( e.sourceData.columnIndex, e.targetData.columnIndex );
		this.state.noHighlights();
		this.model.set( "ui:columnIndex", e.sourceData.columnIndex );
	}.bind(this);
	
	return [
		{ pattern : "fired:dragstart:row"   		, handler : onReorderDragStart 			},
		{ pattern : "fired:dragend:row"      		, handler : onReorderDragEnd   			},
		{ pattern : "fired:dragover:row:row" 		, handler : onReorderDragOver 			},
		{ pattern : "fired:dragleave:row:row"		, handler : onReorderDragLeave			},
		{ pattern : "fired:dragdrop:row:row" 		, handler : onRowToRowDragDrop			},
		{ pattern : "fired:dragstart:column"       	, handler : onReorderDragStart       	},
		{ pattern : "fired:dragend:column"         	, handler : onReorderDragEnd         	},
		{ pattern : "fired:dragover:column:column" 	, handler : onReorderDragOver        	},
		{ pattern : "fired:dragleave:column:column"	, handler : onReorderDragLeave       	},
		{ pattern : "fired:dragdrop:column:column" 	, handler : onColumnToColumnDragDrop 	}
	]
};
	
MatrixInteractions.prototype.__registerSelectionDragAndDrops = function() {
	var onSelectionDragStart = function(e) {
		this.model.set({
			"ui:dragColor" : e.data.color,
			"ui:dragBackground" : e.data.background
		});
	}.bind(this);
	var onSelectionDragEnd = function(e) {
		this.model.set({
			"ui:dragColor" : null,
			"ui:dragBackground" : null
		});
	}.bind(this);
	var onSelectionToColumnDragEnter = function(e) {
		d3.select( e.targetElement )
			.style( "background", this.model.get( "ui:dragBackground" ) );
	}.bind(this);
	var onSelectionToColumnDragLeave = function(e) {
		d3.select( e.targetElement )
			.style( "background", null );
	}.bind(this);
	var onSelectionToColumnDragDrop = function(e) {
		onSelectionToColumnDragLeave(e);
		var columnIndex = e.targetData.columnIndex;
		var selectionIndex = e.sourceData.selectionIndex;
		this.state.columnSelections( columnIndex, selectionIndex );
		this.state.columnHighlights( columnIndex );
		this.model.set( "ui:selectionIndex", selectionIndex );
	}.bind(this);
	
	return [
		{ pattern : "fired:dragstart:selection"       , handler : onSelectionDragStart         },
		{ pattern : "fired:dragend:selection"         , handler : onSelectionDragEnd           },
		{ pattern : "fired:dragenter:selection:column", handler : onSelectionToColumnDragEnter },
		{ pattern : "fired:dragleave:selection:column", handler : onSelectionToColumnDragLeave },
		{ pattern : "fired:dragdrop:selection:column" , handler : onSelectionToColumnDragDrop  }
	];
};

MatrixInteractions.prototype.__initInteractions = function() {
	var interactionHandler = function( e, data ) {
		if ( e.substr( 0, 6 ) === "fired:" )
			for ( var i = 0; i < interactions.length; i++ )
				if ( e.search( interactions[i].pattern ) >= 0 )
					interactions[i].handler( data );
	}.bind( this );
	
	var interactions = [];
	Array.prototype.push.apply( interactions, this.__registerMouseInteractions() );
	Array.prototype.push.apply( interactions, this.__registerReorderingDragAndDrops() );
	Array.prototype.push.apply( interactions, this.__registerSelectionDragAndDrops() );
	this.on( "all", interactionHandler );
};
