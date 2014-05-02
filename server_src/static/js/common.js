/**
 * @param{SELECT} srcElement
 **/
var onSelectDataset = function(srcElement) {
	selectDataset(srcElement.value);
};

/**
 * @param{SELECT} srcElmement
 **/
var onSelectModel = function(srcElement) {
	selectModel(srcElement.value);
};

/**
 * @param{SELECT} srcElmement
 **/
var onSelectAttribute = function(srcElement) {
	selectAttribute(srcElement.value);
};

/**
 * @param {string} [dataset]
 * @param {string} [model]
 * @param {string} [attribute]
 * @return {string}
 **/
var loadPage = function(dataset, model, attribute) {
	var server = configs.server;
	if (dataset && model && attribute) {
		window.location.href = "http://" + server + "/" + dataset + "/" + model + "/" + attribute;
	}
	else if (dataset && model) {
		window.location.href = "http://" + server + "/" + dataset + "/" + model;
	}
	else if (dataset) {
		window.location.href = "http://" + server + "/" + dataset;
	}
	else {
		window.location.href = "http://" + server;
	}
};

/**
 * @param {string} dataset
 **/
var selectDataset = function(dataset) {
	if (dataset && (dataset !== "NONE") && (dataset !== configs.dataset)) {
		loadPage(dataset);
	}
	else {
		loadPage();
	}
};

/**
 * @param {string} model
 **/
var selectModel = function(model) {
	if (model && (model !== "NONE") && (model !== configs.model)) {
		loadPage(configs.dataset, model);
	}
	else {
		loadPage(configs.dataset);
	}
};

/**
 * @param {string} attribute
 **/
var selectAttribute = function(attribute) {
	if (attribute && (attribute !== "NONE")) {
		loadPage(configs.dataset, configs.model, attribute);
	}
	else {
		loadPage(configs.dataset, configs.model);
	}
};
