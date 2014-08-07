var Controls = function(args) {
	switch(args.type) {
		case 'select':
			this.makeDropdown(args)
			break
		
		case 'slider':
			this.makeSlider(args)
			break	
	}
}

Controls.prototype.makeDropdown = function(args) {
	var self = this
	var wrapper = $('<div class="control" id=' + args.id + '>').appendTo('#' + args.wrapper)
	wrapper.append($('<span/>').text(args.label + ': ').attr('class', 'control-text'))
	var select = $('<select>').appendTo(wrapper)
		.attr("id",args.id)
	$(args.options).each(function() {
		select.append($("<option>")
				.attr("value", this.id)
				.attr("id", this.id)
				.text(this.value))
	
	})
	select.val(args.default);
	select.change(args.change)
}

Controls.prototype.makeSlider = function(args) {
	var self = this
	
	var wrapper = $('<div class="control" id=' + args.id + '>').appendTo('#' + args.wrapper)
	wrapper.append($('<span/>').text(args.label + ': ')).attr('class', 'control-text')
	
	var select = $('<div>').appendTo(wrapper)
		.attr("id",args.id + '-slider')
		
	select.slider({
		value:args.default,
		min:args.min, 
		max:args.max, 
		width:200,
		step:args.step,
		change:args.change,
		slide:args.slide
	})
}
