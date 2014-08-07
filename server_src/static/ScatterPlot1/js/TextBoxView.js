var TextBoxView = Backbone.View.extend({
	el:'#main',
	defaults:{
			width:400, 
			height:400, 	
		
		},
	initialize:function(options) {
		this.options = _.extend({}, this.defaults, options)
		this.sizeView()
		var textId = this.model.get('docNum')
		this.viewText = this.model.rawData[textId].doc_content
		this.model.on('change:highlighted', function() {
			var textId = this.model.get('highlighted')
			this.viewText = this.model.rawData[textId].doc_content
			console.log('view text ', this.viewText)
			this.textBox.updateText(this.viewText)
		}, this)
		this.render()
	},
	render:function() {
		var that = this
		this.textBox = new TextBox(this.loadSettings())
	}

})

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
TextBoxView.prototype.sizeView = function() {
	var that = this
	that.options.width = $(window).width()/3
	that.options.height = $(window).height() - $('#top-controls').height() - 10
	that.options.position = this.options.position == undefined ? {} : this.options.position
	that.options.position.top = $('#top-controls').height() + 10
	that.options.position.left = $(window).width()*2/3
}