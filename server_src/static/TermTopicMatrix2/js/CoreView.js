var CoreView = Backbone.View.extend();

CoreView.prototype.initialize = function() {
	this.__dirty__ = false;
};

CoreView.prototype.triggerDirty = CoreModel.prototype.triggerDirty;
CoreView.prototype.__isDirty__ = CoreModel.prototype.__isDirty__;
CoreView.prototype.isDirty = CoreModel.prototype.isDirty;
CoreView.prototype.__combineDirty__ = CoreModel.prototype.__combineDirty__;
CoreView.prototype.combineDirty = CoreModel.prototype.combineDirty;
CoreView.prototype.__setDirty__ = CoreModel.prototype.__setDirty__;
CoreView.prototype.setDirty = CoreModel.prototype.setDirty;
CoreView.prototype.__getDirty__ = CoreModel.prototype.__getDirty__;
CoreView.prototype.getDirty = CoreModel.prototype.getDirty;

CoreView.prototype.__eventType = function( identifier ) {
	if ( d3.event.ctrlKey || d3.event.metaKey )
		identifier += "+meta";
	if ( d3.event.altKey )
		identifier += "+alt";
	if ( d3.event.shiftKey )
		identifier += "+shift";
	return identifier;
};

CoreView.prototype.__keyDownHandler = function( data ) {
	var eventType = this.__eventType( "keydown" );
	var eventParamts = data.dataType;
	var eventID = "fired:" + eventType + ":" + eventParams;
	var element = d3.event.srcElement;
	this.trigger( eventID, {
		"event" : d3.event,
		"eventID" : eventID, 
		"eventType" : eventType,
		"eventParams" : eventParams,
		"data" : data, 
		"element" : element
	} );
};

CoreView.prototype.__keyPressHandler = function( data ) {
	var eventType = this.__eventType( "keypress" );
	var eventParamts = data.dataType;
	var eventID = "fired:" + eventType + ":" + eventParams;
	var element = d3.event.srcElement;
	this.trigger( eventID, {
		"event" : d3.event,
		"eventID" : eventID, 
		"eventType" : eventType,
		"eventParams" : eventParams,
		"data" : data, 
		"element" : element
	} );
};

CoreView.prototype.__keyUpHandler = function( data ) {
	var eventType = this.__eventType( "keyup" );
	var eventParamts = data.dataType;
	var eventID = "fired:" + eventType + ":" + eventParams;
	var element = d3.event.srcElement;
	this.trigger( eventID, {
		"event" : d3.event,
		"eventID" : eventID, 
		"eventType" : eventType,
		"eventParams" : eventParams,
		"data" : data, 
		"element" : element
	} );
};

CoreView.prototype.__mouseClickHandler = function( data ) {
	var eventType = this.__eventType( "click" );
	var eventParams = data.dataType;
	var eventID = "fired:" + eventType + ":" + eventParams;
	var element = d3.event.srcElement;
	this.trigger( eventID, {
		"event" : d3.event,
		"eventID" : eventID, 
		"eventType" : eventType,
		"eventParams" : eventParams,
		"data" : data, 
		"element" : element
	} );
	d3.event.cancelBubble = true;
	d3.event.preventDefault();
};

CoreView.prototype.__mouseOverHandler = function( data ) {
	var eventType = this.__eventType( "enter" );
	var eventParams = data.dataType
	var eventID = "fired:" + eventType + ":" + eventParams;
	var element = d3.event.srcElement;
	this.trigger( eventID, {
		"event" : d3.event,
		"eventID" : eventID, 
		"eventType" : eventType,
		"eventParams" : eventParams,
		"data" : data, 
		"element" : element
	} );
};

CoreView.prototype.__mouseOutHandler = function( data ) {
	var eventType = this.__eventType( "exit" );
	var eventParams = data.dataType
	var eventID = "fired:" + eventType + ":" + eventParams;
	var element = d3.event.srcElement;
	this.trigger( eventID, {
		"event" : d3.event,
		"eventID" : eventID, 
		"eventType" : eventType,
		"eventParams" : eventParams,
		"data" : data, 
		"element" : element
	} );
};

CoreView.prototype.__dragStartHandler = function( data ) {
	if ( this.model.get( "ui:dragActive" ) !== true ) {
		d3.event.dataTransfer.effectAllowed = "move";
		d3.event.dataTransfer.setDragImage( document.getElementById("EmptyImage"), 0, 0 );
		var eventType = this.__eventType( "dragstart" );
		var eventParams = data.dataType;
		var eventID = "fired:" + eventType + ":" + eventParams;
		var element = d3.event.srcElement;
		this.model.set({
			"ui:dragActive" : true,
			"ui:dragData" : data,
			"ui:dragElement" : element
		});
		this.trigger( eventID, { 
			"event" : d3.event,
			"eventID" : eventID, 
			"eventType" : eventType, 
			"eventParams" : eventParams,
			"data" : data, 
			"element" : element 
		} );
	}
};

CoreView.prototype.__dragEndHandler = function( data ) {
	var eventType = this.__eventType( "dragend" );
	var eventParams = data.dataType;
	var eventID = "fired:" + eventType + ":" + eventParams;
	var element = d3.event.srcElement;
	this.trigger( eventID, { 
		"event" : d3.event,
		"eventID" : eventID, 
		"eventType" : eventType, 
		"eventParams" : eventParams,
		"data" : data, 
		"element" : element 
	} );
	this.model.set({
		"ui:dragActive" : false,
		"ui:dragData" : null,
		"ui:dragElement" : null
	});
};

CoreView.prototype.__dragEnterHandler = function( data ) {
	if ( this.model.get( "ui:dragActive" ) === true ) {
		var eventType = this.__eventType( "dragenter" );
		var sourceData = this.model.get( "ui:dragData" );
		var targetData = data;
		var eventParams = sourceData.dataType + ":" + targetData.dataType;
		var eventID = "fired:" + eventType + ":" + eventParams;
		var sourceElement = this.model.get( "ui:dragElement" );
		var targetElement = d3.event.srcElement;
		this.trigger( eventID, {
			"event" : d3.event,
			"eventID" : eventID,
			"eventType" : eventType,
			"eventParams" : eventParams,
			"data" : targetData,
			"element" : targetElement,
			"sourceData" : sourceData,
			"sourceElement" : sourceElement,
			"targetData" : targetData,
			"targetElement" : targetElement 
		});
	}
};

CoreView.prototype.__dragOverHandler = function( data ) {
	if ( this.model.get( "ui:dragActive" ) === true ) {
		if ( d3.event.preventDefault ) { d3.event.preventDefault() }
		d3.event.dataTransfer.dropEffect = "move";
		var eventType = this.__eventType( "dragover" );
		var sourceData = this.model.get( "ui:dragData" );
		var targetData = data;
		var eventParams = sourceData.dataType + ":" + targetData.dataType;
		var eventID = "fired:" + eventType + ":" + eventParams;
		var sourceElement = this.model.get( "ui:dragElement" );
		var targetElement = d3.event.srcElement;
		this.trigger( eventID, {
			"event" : d3.event,
			"eventID" : eventID,
			"eventType" : eventType,
			"eventParams" : eventParams,
			"data" : targetData,
			"element" : targetElement,
			"sourceData" : sourceData,
			"sourceElement" : sourceElement,
			"targetData" : targetData,
			"targetElement" : targetElement 
		});
	}
};

CoreView.prototype.__dragLeaveHandler = function( data ) {
	if ( this.model.get( "ui:dragActive" ) === true ) {
		var eventType = this.__eventType( "dragleave" );
		var sourceData = this.model.get( "ui:dragData" );
		var targetData = data;
		var eventParams = sourceData.dataType + ":" + targetData.dataType;
		var eventID = "fired:" + eventType + ":" + eventParams;
		var sourceElement = this.model.get( "ui:dragElement" );
		var targetElement = d3.event.srcElement;
		this.trigger( eventID, {
			"event" : d3.event,
			"eventID" : eventID,
			"eventType" : eventType,
			"eventParams" : eventParams,
			"data" : targetData,
			"element" : targetElement,
			"sourceData" : sourceData,
			"sourceElement" : sourceElement,
			"targetData" : targetData,
			"targetElement" : targetElement 
		});
	}
};

CoreView.prototype.__dropHandler = function( data ) {
	if ( this.model.get( "ui:dragActive" ) === true ) {
		var eventType = this.__eventType( "dragdrop" );
		var sourceData = this.model.get( "ui:dragData" );
		var targetData = data;
		var eventParams = sourceData.dataType + ":" + targetData.dataType;
		var eventID = "fired:" + eventType + ":" + eventParams;
		var sourceElement = this.model.get( "ui:dragElement" );
		var targetElement = d3.event.srcElement;
		this.trigger( eventID, {
			"event" : d3.event,
			"eventID" : eventID,
			"eventType" : eventType,
			"eventParams" : eventParams,
			"data" : targetData,
			"element" : targetElement,
			"sourceData" : sourceData,
			"sourceElement" : sourceElement,
			"targetData" : targetData,
			"targetElement" : targetElement 
		});
	}
};

CoreView.prototype.keystrokeListeners = function(e) {
	e.on( "keydown", this.__keyDownHandler.bind(this) )
	 .on( "keypress", this.__keyPressHandler.bind(this) )
	 .on( "keyup", this.__keyUpHandler.bind(this) )
};

CoreView.prototype.mouseListeners = function(e) {
	e.style( "pointer-events", "auto" )
	 .on( "click", this.__mouseClickHandler.bind(this) )
	 .on( "mouseover", this.__mouseOverHandler.bind(this) )
	 .on( "mouseout", this.__mouseOutHandler.bind(this) )
};

CoreView.prototype.dragdropListeners = function(e) {
	e.style( "pointer-events", "auto" )
	 .attr( "draggable", true )
	 .on( "dragstart", this.__dragStartHandler.bind(this) )
	 .on( "dragend", this.__dragEndHandler.bind(this) )
	 .on( "dragover", this.__dragOverHandler.bind(this) )
	 .on( "dragenter", this.__dragEnterHandler.bind(this) )
	 .on( "dragleave", this.__dragLeaveHandler.bind(this) )
	 .on( "drop", this.__dropHandler.bind(this) )
};
