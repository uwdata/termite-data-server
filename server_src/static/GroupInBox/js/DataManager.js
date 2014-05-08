/**
 * Create a data structure that holds "modelID" and "termLimit".
 * @constructor
 **/
var DataManager = Backbone.Model.extend({
	defaults : {
		"modelID" : undefined,
		"termLimit" : undefined,
		"modelIDs" : [
			"nsf1k_mallet",
			"nsf10k_mallet",
			"nsf25k_mallet",
			"nsf146k_mallet",
			"20newsgroups_mallet"
		],
		"termLimits" : [ 5, 7, 10, 15, 20 ] 
	}
});

/**
 * @constructs
 **/
DataManager.prototype.initialize = function() {
	this.update = _.debounce( this.__update, 10 );
	
	this.view = new DataManagerView({ model: this });
	
	this.readQueryString();
	this.on( "change", this.update, this );
	this.on( "change", this.writeQueryString, this );
};

/**
 * @constant
 * @type {string}
 **/
DataManager.prototype.DEFAULT_MODEL_ID = "nsf1k_mallet";

/**
 * @constant
 * @type {number}
 **/
DataManager.prototype.DEFAULT_TERM_LIMIT = 10;

/**
 * @private
 **/
DataManager.prototype.__update = function() {
	var modelID = this.get("modelID");
	var termLimit = this.get("termLimit");
	this.trigger("update", modelID, termLimit);
};

/**
 * @private
 **/
DataManager.prototype.writeQueryString = function() {
	var modelID = this.get("modelID");
	var termLimit = this.get("termLimit");
	var query = [];
	if ( modelID !== this.DEFAULT_MODEL_ID ) {
		query.push( "m=" + modelID );
	}
	if ( termLimit !== this.DEFAULT_TERM_LIMIT ) {
		query.push( "n=" + termLimit );
	}
	var url = window.location.origin + window.location.pathname;
	if ( query.length > 0 ) {
		url += "?" + query.join("&");
	}
	history.pushState( null, null, url );
};

/**
 * @private
 **/
DataManager.prototype.readQueryString = function() {
	var queryString = window.location.search.substr(1);
	var keysAndValues = {};
	var rePlus = /\+/g;
	var reKeysAndValues = /([^&=]+)=?([^&]*)/g;
	var decode = function ( str ) { return decodeURIComponent( str.replace( rePlus, " " ) ) };
	for ( var i = 0; i < 2; i++ ) {
		var match = reKeysAndValues.exec( queryString );
		if ( match ) {
			var key = decode( match[1] );
			var value = decode( match[2] );
			keysAndValues[ key ] = value;
		}
		else {
			break;
		}
	}
	var modelID = this.DEFAULT_MODEL_ID;
	var termLimit = this.DEFAULT_TERM_LIMIT;
	if ( keysAndValues.hasOwnProperty("m") ) {
		modelID = keysAndValues["m"];
	}
	if ( keysAndValues.hasOwnProperty("n") ) {
		termLimit = parseInt(keysAndValues["n"], 10);
	}
	this.set({
		"modelID" : modelID,
		"termLimit" : termLimit
	});
};

/**
 * Creates an UI for specifying topic model and the number of top terms per topic.
 * @constructor
 **/
var DataManagerView = Backbone.View.extend({
	el : "div.DataManager"
})

/**
 * @constructs
 **/
DataManagerView.prototype.initialize = function() {
	this.refresh = _.debounce( this.__refresh, 10 );
	
	var modelID = this.model.get("modelID");
	var termLimit = this.model.get("termLimit");
	var modelIDs = this.model.get("modelIDs");
	var termLimits = this.model.get("termLimits");
	var container = d3.select(this.el);
	container.html("Show model <select class='ModelID'></select> with top <select class='TermLimit'></select> terms.");
	container.select("select.ModelID")
		.on("change", function() { this.model.set("modelID", d3.event.target.value) }.bind(this))
		.selectAll("option").data(modelIDs).enter().append("option")
			.attr("value", function(d) { return d })
			.attr("selected", function(d) { return d === modelID ? "selected" : null })
			.text(function(d) { return d });
	container.select("select.TermLimit")
		.on("change", function() { this.model.set("termLimit", parseInt(d3.event.target.value)) }.bind(this))
		.selectAll("option").data(termLimits).enter().append("option")
			.attr("value", function(d) { return d })
			.attr("selected", function(d) { return d === termLimit ? "selected" : null })
			.text(function(d) { return d });
			
	this.model.on( "change:modelID change:termLimit", this.refresh, this );
};

/**
 * @private
 **/
DataManagerView.prototype.__refresh = function() {
	var modelID = this.model.get("modelID");
	var termLimit = this.model.get("termLimit");
	var container = d3.select(this.el);
	container.select("select.ModelID").node().value = modelID;
	container.select("select.TermLimit").node().value = termLimit;
};
