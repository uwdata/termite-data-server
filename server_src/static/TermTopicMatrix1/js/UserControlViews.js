// All Views expect to be bound to the state model

// displays number of terms that are visible (unique terms in affinity, saliency, and user defined)
var TotalTermsView = Backbone.View.extend({
	el : 'div.TotalTermsView',
	render : function()
	{
		d3.select(this.el).text( this.model.get("totalTerms") );
	}
});

// displays number of terms by Affinity that are shown
var AffinityNumTermsView = Backbone.View.extend({
	el : 'div.AffinityNumTermsView',
	render : function()
	{
		d3.select(this.el).text( this.model.get("numAffinityTerms") );
	}
});

// displays slider for number of terms by Affinity that are shown
var AffinityNumTermsSlider = Backbone.View.extend({
	el : 'input.AffinityNumTermsSlider',
	events : {
		'change' : function(e) {
			this.model.set("numAffinityTerms", parseInt(e.target.value));
		}
	},
	initialize : function() {
		this.model.on( "change:numAffinityTerms", function(value) {
			d3.select(this.el)[0][0].value = this.model.get("numAffinityTerms");
		}, this);
	}
});

// displays number of terms by Saliency that are shown
var SalientNumTermsView = Backbone.View.extend({
	el : 'div.SalientNumTermsView',
	render : function()
	{
		d3.select(this.el).text( this.model.get("numSalientTerms") );
	}
});

// displays slider for number of terms by Saliency that are shown
var SalientNumTermsSlider = Backbone.View.extend({
	el: 'input.SalientNumTermsSlider',
	events : {
		'change' : function(e) {
			this.model.set("numSalientTerms", parseInt(e.target.value));
		}
	},
	initialize : function() {
		this.model.on( "change:numSalientTerms", function(value) {
			d3.select(this.el)[0][0].value = this.model.get("numSalientTerms");
		}, this);
	}
});

// handles user defined persistent terms by multi-select box with populated options
var MultiSelectTermsBox = Backbone.View.extend({
	el: 'select.multiSelectTerms',
	events : {
		'change' : function(e) {
			var visTerms = $(".multiSelectTerms").val();
			if(visTerms === null)
				visTerms = [];
			this.model.setVisibleTerms(visTerms);
		}
	},
	render : function() {
		if( this.model.get("visibleTerms").length > 0 ){
			var visTermsList = this.model.get("visibleTerms");
			var optionsList = d3.select("#multi-select")[0][0].options;
			for(var i = 0; i < visTermsList.length; i++) {
				var visTerm = visTermsList[i];
				for( var j = 0; j < optionsList.length; j++){
					if( optionsList[j].text === visTerm ){
						optionsList[j].selected = true;
						break;
					}
				}
			}
			$("#multi-select").trigger("liszt:updated");
		}
	}
});

// displays version of the last loaded state
var CurrentVersionNo = Backbone.View.extend( {
	el: 'div.currentVersionNo',
	render : function()
	{
		d3.select(this.el).text( this.model.get("version") );
	}
});

// handles button to save state
var SaveStateButton = Backbone.View.extend({
	el: 'button.saveState',
	events : {
		'click' : function(e) {
			saveStatetoDB();
		}
	}
});

// handles button to load last saved state
var LoadStateButton = Backbone.View.extend({
	el: 'button.loadState',
	events : {
		'click' : function(e) {
			loadStatefromDB( false );
		}
	}
});

// checkbox to toggle normalizing by topic weights
var NormalizeColumns = Backbone.View.extend({
	el: 'input.NormalizeColumns',
	events : {
		'change' : function(e) {
			this.model.set("normColumns", e.target.checked);
		}
	},
	initialize : function() {
		this.model.on( "change:normColumns", function(value) {
			d3.select(this.el)[0][0].checked = this.model.get("normColumns");
		}, this);
	}
});

// checkbox to toggle adding top twenty terms of every selected topic
var AddTopTwenty = Backbone.View.extend({
	el: 'input.TopTwentyAddition',
	events : {
		'change' : function(e) {
			this.model.set("addTopTwenty", e.target.checked);
		}
	},
	initialize : function() {
		this.model.on( "change:addTopTwenty", function(value) {
			d3.select(this.el)[0][0].checked = this.model.get("addTopTwenty");
		}, this);
	}
});

// displays feedback as to what sort is being applied if any
var SortDescription = Backbone.View.extend({
	el: 'div.SortDescription',
	render : function()
	{
		var sort = this.model.get("sortType");
		var topic = this.model.get("doubleClickTopic");
		var output = "";
		if( sort === "" )
			output = "default";
		else if (sort === "asc")
			output = "ascending on topic #" + topic;
		else
			output = "descending on topic #" + topic;
		d3.select(this.el).text( output );
	},
	initialize : function() {
		this.model.on( "change:sortType change:doubleClickTopic", function(value) {
			this.render();
		}, this);
	}
});

// handles button to clear current sorting method if not default
var ClearSortButton = Backbone.View.extend({
	el: 'button.clearSort',
	events : {
		'click' : function(e) {
			this.model.clearSorting();
		}
	}
});

// handles button to clear all current topic selections
var ClearAllButton = Backbone.View.extend({
	el: 'button.clearAll',
	events : {
		'click' : function(e) {
			this.model.clearAllSelectedTopics();
		}
	}
});

// handles relabelling topics button and input box
var TopicRenameButton = Backbone.View.extend({
	el: 'button.saveRename',
	inputTopicName: 'input.rename',
	inputTopicId: null,
	events : {
		'click' : function(e) {
			if( this.inputTopicId === null || this.inputTopicName === "")
				return;
			this.model.updateLabel(this.inputTopicId, d3.select(this.inputTopicName)[0][0].value);
		}
	},
	render : function(options) {
		var topicMapping = _.object(_.map(this.model.get("topicIndex"), function(item){ return [item.id, item] }));
		this.inputTopicId = topicMapping[options.topic].position;
		d3.select(this.inputTopicName)[0][0].value = topicMapping[options.topic].name;
	}, 
	clear : function( options ) {	// clears input box on clearAllTopicSelections event
		this.inputTopicId = null;
		d3.select(this.inputTopicName)[0][0].value = "";
	}
});

// handles reordering topics button and input box
// TODO: do not need this user control if change to drag and drop
var TopicMoveButton = Backbone.View.extend({
	el: 'button.saveMove',
	inputTopicNo: 'input.moveTopicNo',
	inputPosition: 'input.topicPosition',
	events : {
		'click' : function(e) {
			this.model.moveTopic( d3.select(this.inputTopicNo)[0][0].value, d3.select(this.inputPosition)[0][0].value );
		}
	}
});

// handles resetting to original (id) order button
var ClearMoveButton = Backbone.View.extend({
	el: 'button.clearMoves',
	events : {
		'click' : function(e) {
			this.model.originalPositions();
		}
	}
});

// handles displaying or hiding instructions in the user control panel
var ShowInstructionsButton = Backbone.View.extend({
	el: 'button.showInstructions',
	status: true,
	events : {
		'click' : function() {
			if( this.status ) {
				$(".instructions").animate({ height: '+=20'}, 500);
				this.status = false;
				d3.select(this.el)[0][0].innerHTML = "Hide Instructions";
			}
			else {
				$(".instructions").animate({ height: '-=20'}, 500);
				this.status = true;
				d3.select(this.el)[0][0].innerHTML = "Show Instructions";
			}
		}
	}
});

