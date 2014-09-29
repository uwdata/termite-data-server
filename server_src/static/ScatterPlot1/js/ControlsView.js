var ControlsView = Backbone.View.extend({
	initialize:function() {
		var that = this
		this.model = sm
		var that = this
		
		// Change functions
		this.changeTopicFunction = function(value) {
			that.model.set('topic', this.value)
		}
		this.changeXvariableFunction = function(value) {
			that.model.set('xVariable', this.value)
		}
		this.changeColorVariableFunction = function(value) {
			that.model.set('colorVariable', this.value)
		}
		var changeOpacityFunction = function(event, ui) {
			that.model.set('opacity', ui.value)
		}
		var changeRadiusFunction = function(event, ui) {
			that.model.set('radius', ui.value)
		}
		this.prepData()
		
		// Build new controls
		this.topicControls =  new Controls(this.controlSettings.topic)
		this.xVariableControls =  new Controls(this.controlSettings.xVariable)
		this.colorVariableControls =  new Controls(this.controlSettings.colorVariable)
	}, 
	prepData:function() {
		var that = this
		that.terms = {}
			topTerms.TopicList.map(function(d) {
			that.terms[d.topic_index] = d.topic_desc
		})
		this.controlSettings = {}
		this.controlSettings.topic = {
			id:'topic', 
			label:'Topic',
			type:'select', 
			wrapper:'top-controls', 
			options:d3.keys(this.terms).map(function(d) {
				return {id:d, value:'Topic ' + Number(Number(d) + 1) + ' (' + that.terms[d] + ')'}
			}), 
			default:sm.get('topic'),
			change:that.changeTopicFunction
		}
		
		this.controlSettings.xVariable = {
			id:'xvariable', 
			label:'X Variable', 
			type:'select',
			wrapper:'top-controls',
			options:that.model.variables.filter(function(d) {return d.name!='date' && d.name!='blog'}).map(function(d) {return {id:d.field_name, value:d.field_name}}), 
			default:sm.get('xVariable'), 
			change:that.changeXvariableFunction
		}
	
		var options = [{id:'none', value:'none'}]
		that.model.variables.filter(function(d) {return d.name!='date' && d.name!='blog'}).map(function(d) {options.push({id:d.field_name, value:d.field_name})})
		this.controlSettings.colorVariable = {
			id:'colorvariable', 
			label:'Color', 
			type:'select',
			wrapper:'top-controls',
			options:options, 
			default:sm.get('colorVariable'), 
			change:that.changeColorVariableFunction
		}
	}

})