var configs = {{WriteJSON(configs)}};
var params = {{WriteJSON({key : value for key, value in params.iteritems() if value is not None})}};

var updateParamTextArea = function(name, srcElement) {
	var value = srcElement.value;
	changeParam(name, value);
};

var updateParamTextInput = function(name, srcElement) {
	var value = srcElement.value;
	changeParam(name, value);
};

var updateParamRange = function(name, srcElement) {
	var valueSqrt = parseInt(srcElement.value, 10);
	var valueNum = valueSqrt === -1 ? -1 : parseInt(valueSqrt*valueSqrt/1000/1000);
	var value = (valueNum === -1 ? null : valueNum);
	var valueStr = (valueNum === -1 ? "&mdash;" : valueNum);
	d3.select("."+name).html(valueStr);
	changeParam(name, value);
};

var updateParamSelect = function(name, srcElement) {
	var valueRaw = srcElement.value;
	var value = valueRaw === "NONE" ? null : valueRaw;
	changeParam(name, value);
};

var updateParamFormat = function(srcElement) {
	var valueRaw = srcElement.value;
	var value = valueRaw === "NONE" ? null : valueRaw;
	changeParam('format', value);
};
