// Model

var ScatterModel = Backbone.Model.extend({
	initialize:function() {
		// this.loadData()
	},
	defaults:{
		group1:'rating', 
		docNum:257,
		highlighted:257, 
		docLimit:QueryString.limit == undefined ? 100 : QueryString.limit
	}, 
	prep:function(callback) {
		var that = this
		that.terms = {}
		console.log(this.variables, MetadataFields.MetadataFields)
		var type = this.variables.filter(function(d) {return d.field_name == that.get('xVariable')}).map(function(d) {return d.field_type})
		var colorType = this.variables.filter(function(d) {return d.field_name == that.get('colorVariable')}).map(function(d) {return d.field_type})
		that.set('xVariableType', type)
		that.set('colorVariableType', colorType)
		
		// Format terms
		topTerms.TopicList.map(function(d) {
			that.terms[d.id] = d.topic_desc
		})
		
		
		// Prep proportions
		this.topicProportions = {}
		this.rawProportions.filter(function(d){return d.topic_index == that.get('topic')}).map(function(d,i) {that.topicProportions[i] = d.value})
		
		// Get ranges of the xvariable and color variable to set scales
		this.xLabels = []
		this.colorLabels = []
		d3.range(0,1000).map(function(i) {
			var xLabel = Metadata[that.get('xVariable')].MetadataValues[i].value
			var colorLabel = that.get('colorVariable') == 'none' ? 'none' : Metadata[that.get('colorVariable')].MetadataValues[i].value
			if(that.xLabels.indexOf(xLabel) == -1) that.xLabels.push(xLabel)
			if(that.colorLabels.indexOf(colorLabel) == -1) that.colorLabels.push(colorLabel)
		})
		this.colorLabels.sort(function(a,b) {return a - b})
		if(this.get('xVariableType') !='integer') this.xLabels.sort(function(a,b) {return a.toUpperCase() > b.toUpperCase()})
		
		// Prep Data for View
		this.data = d3.range(0, 1000).map(function(i) {
			var prop = that.topicProportions[i] == undefined? 0 : that.topicProportions[i]
			var xVar = that.get('xVariable')
			var colorVar = that.get('colorVariable')
 			var colorValue = colorVar == 'none' ? 'none' : Metadata[that.get('colorVariable')].MetadataValues[i].value
			var groupVar = that.get('group1')
			var xLabel = Metadata[xVar].MetadataValues[i].value
			var xValue = that.get('xVariableType') !='integer' ? that.xLabels.indexOf(xLabel) : xLabel
			return {id:i, 
 				proportion:prop,
				xVar:xVar, 
				xValue:xValue,
				colorVar:colorVar, 
				colorValue:colorValue,
				xLabel:xLabel,
			}
		})
		if(typeof callback == 'function') callback()

		// assign events
		this.on('clickCircle', function(d){
			this.set('highlighted', d)
		})
	}, 
})


ScatterModel.prototype.loadData = function(callback) {	
	this.rawData = Documents.Documents
	this.rawProportions = proportions.DocTopicMatrix
	this.variables = MetadataFields.MetadataFields
	this.set('xVariable', this.variables[0].field_name)
	this.set('colorVariable', this.variables[1].field_name)
	this.set('xVariableType', this.variables[0].field_type)
	this.set('colorVariableType', this.variables[1].field_type)
	this.prep(callback)
}