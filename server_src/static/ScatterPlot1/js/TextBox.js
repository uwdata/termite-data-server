var TextBox = function(settings) {
	this.settings = settings
	this.div = d3.select('#' + settings.container).append('div')
		.attr('id', settings.id).attr('class', 'textbox')
		.style('height', this.settings.height + 'px')
		.style('width', this.settings.width + 'px')
		.style('position', 'absolute')
		.style('top', this.settings.position.top + 'px')
		.style('left', this.settings.position.left + 'px')
		
	this.build()
}

TextBox.prototype.build = function() {
	this.g = this.div.append('g')
		.attr('id', this.settings.id + '-g')
		
		
	this.div.text(this.settings.text)
}

TextBox.prototype.updateText = function(text) {
	this.div.text(text)

}

TextBox.prototype.updatePosition = function(settings) {
	var that = this
	this.settings = settings
	this.div.transition().duration(500)
		.style('height', this.settings.height + 'px')
		.style('width', this.settings.width + 'px')
		.style('top', this.settings.position.top + 'px')
		.style('left', this.settings.position.left + 'px')
	

}