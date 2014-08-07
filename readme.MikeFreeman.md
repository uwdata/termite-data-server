Termite Explorer
============================

Termite Explorer is a visual tool built in an MVC framework that allows users to view results of their topic models and identify the individual documents.  

The tool is comprised of two components:

* Interactive scatterplot: This chart plots a point for each document, where the x-axis is a selected covariate based on the document's metadata, and the y-axis is the model's estimated proportion of a selected topic.  It also provides the option of coloring each point.
* Document Viewer: A selected document's corpus is shown in the document viewer on the right.

These two charts work in tandem in that any document can be clicked to be viewed in the document viewer.  Each portion of the visualization is an independent View that has a data Model and uses a charting function to render the visual components.


Scatterplot
--------------

The scatterplot is an instantiation of the view [ScatterView](https://github.com/mkfreeman/termite-dev/blob/master/js/ScatterView.js) and has a data model [ScatterModel](https://github.com/mkfreeman/termite-dev/blob/master/js/ScatterModel.js).  The chart layout and representation is powered by the [Scatter](https://github.com/mkfreeman/termite-dev/blob/master/js/scatter.js) function.

The ScatterView formats the data from the ScatterModel and passes it to the Scatter function.  The Scatter function expects is powered by an array of objects (each corresponding to a single data point), each with the following data attributes:

| Variable      | Type          | Functionality |
| ------------- |:-------------:| :-----|
| id    				| integer		| The value is used to identify the document which is clicked or hovered over|
| x			   			| numeric    	| This dictates the position along the x-axis |
| y 					| numeric (0 < y < 1)| This dictates the position along the y-axis, and is bound by 0 and 1.|
| color (optional)		| string (color)| This assigns the color value to the point, used when color scale is categorical |
| colorValue (optional) | numeric       | This is used to calculate the color if the color range is continuous.|


The ScatterModel (the data for ScatterView) prepares data for both the ScatterView and ControlsView.  The data is currently accessed from static files, and assigned to static variables (line 84):
```javascript
// Documents is defined in data as response from http://termite.jcchuang.org/poliblogs_stm/corpus/Documents?format=json&docLimit=5000
// proportions is defined in data as response from http://termite.jcchuang.org/poliblogs_stm/lda/DocTopicMatrix?format=json&docLimit=5000

ScatterModel.prototype.loadData = function(callback) {	
	this.rawData = Documents.Documents
	this.rawProportions = proportions.DocTopicMatrix
	this.prep(callback)
}
```

Topic proportions are then filtered down for the specific topic (line 38, ScatterModel.js):

```javascript
// Prep proportions
		this.topicProportions = {}
		this.rawProportions.filter(function(d){return d.topic == that.get('topic')}).map(function(d) {that.topicProportions[d.docID] = d.value})

```

These values are then prepped into a data object for the view (line 54, ScatterModel.js):
```javascript
// Prep Data for View
this.data = this.rawData.map(function(d,i) {
	var prop = that.topicProportions[d.DocID] == undefined? 0 : that.topicProportions[d.DocID]
	var content = d.DocContent
	var xVar = that.get('xVariable')
	var colorVar = that.get('colorVariable')
	var colorValue = colorVar == 'none' ? 'none' : d[colorVar]
	var groupVar = that.get('group1')
	var xLabel = d[xVar]
	var xValue = that.get('xVariableType') !='integer' ? that.xLabels.indexOf(xLabel) : xLabel
	var groupValue =d[groupVar]
	return {id:i, 
		proportion:prop,
		content:content, 
		xVar:xVar, 
		xValue:xValue,
		colorVar:colorVar, 
		colorValue:colorValue,
		xLabel:xLabel,
	}
})
```

There is only minor object manipulation within the ScatterView before passing to the Scatter function (line 59, ScatterView.js):
```javascript
prepData:function() {
	var that = this
	this.chartData = []
	this.model.data.map(function(d,i) {
		var color =  'blue'
		that.chartData.push({
			id:d.id, 
			x:isFinite(d.xValue) ? Number(d.xValue) : d.xValue, 
			colorValue:d.colorValue,
			y:Number(d.proportion), 
			color:color
		})
	})	
},
```

TextBox
--------------
The document body is an instantiation of the [TextBoxView](https://github.com/mkfreeman/termite-dev/blob/master/js/TextBoxView.js) which uses the [TextBox](https://github.com/mkfreeman/termite-dev/blob/master/js/TextBox.js) function to render the corpus.

The TextBoxView formats the following variables to pass to the TextBox function

| Variable      | Type          | Functionality |
| ------------- |:-------------:| :-----|
| id    				| integer		| The value is used to identify the document which is currently selected.|
| text			   		| string    	| This is the document body that renders as the text on the screen. |
| width					| numeric 	    | This is the pixel width of the TextBox|
| height				| numeric 		| This is the pixel height of the TextBox |
| position				| numeric       | Object with attributes "left" and "top" for positioning of the TextBox|
| container				| string        | Wrapper div on the page that the textbox will be appended to.|


The formatting is done here (line 27, TextBoxView.js):
```javascript
TextBoxView.prototype.loadSettings = function() {
	return {
		text:this.viewText,
		container:this.el.id, 
		id:this.textid,
		width:this.options.width, 
		height:this.options.height, 
		position:this.options.position

	}
}

```
The TextBoxView is also powered by the ScatterModel as the data, and isolates the corpus by referencing the current docNum attribute of the ScatterModel (line 11, TextBoxView.js)
```javascript
var textId = this.model.get('docNum')
this.viewText = this.model.data[textId].content
```

Controls
--------------
The Controls (Topic, X Variable, and Color) options are powered by the ControlsView and use the Controls file to render the menus.  This data for the Controls is also the ScatterModel object.

**Topic**

The data for the topic menu are prepared in the ScatterModel object (line 27, ScatterModel.js):

```javascript
// topTerms is defined as response from: http://termite.jcchuang.org/poliblogs_stm/lda/TopTerms?format=json
// Format terms
topTerms.TopTerms.map(function(d) {
	that.terms[d.topic] = that.terms[d.topic] == undefined ? [] : that.terms[d.topic]
	that.terms[d.topic].push({term:d.term, value:d.value})
})

// Sort terms
d3.keys(that.terms).map(function(d) {
	that.terms[d].sort(function(a,b) {return a.value - b.value})
})

```

**X Variable and Color options**

The X Variable and Color menu data (options) is currently set in the ScatterModel (line 21, ScatterModel.js):
```javascript
// Documents is defined in data as response from http://termite.jcchuang.org/poliblogs_stm/corpus/Documents?format=json&docLimit=5000
that.variables = Documents.Metadata.filter(function(d) {return d.name.indexOf("Doc")==-1})
```

All views are instantiated in the index.html once the data for the model has loaded (line 68, index.html)
```javascript
sm.loadData(function() {
	cv = new ControlsView()
	sv = new ScatterView({model:sm, el:'#main', chartid:'scatter-' + d, textid:'text-' + d})
	tv = new TextBoxView({model:sm, el:'#main', textid:'text-' + d})
})
```

