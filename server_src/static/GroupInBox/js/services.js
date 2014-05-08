'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('termite.services', [])
	.factory("TopicModelService", function ($http, $rootScope) {
		var TopicModelService = {};

		TopicModelService.topicModelId = null;
		TopicModelService.topicModel = null;

		TopicModelService.getTopicModel = function (id, terms) {
			$rootScope.$broadcast("topic-model-loading");
			var data = {
				"termLimit" : NUM_TERMS
			}
			var url = SERVER_URL;
			console.log("[LOADING]", "URL", url, "DATA", data);
			$http({
				url : url,
				data : $.param(data),
				method : 'POST',
				headers: {'Content-Type': 'application/x-www-form-urlencoded'}
			})
				.success(function (data, status, headers, config) {
					console.log("[LOADED]", "URL", url, "Results:", status, "Data:", data);
					TopicModelService.topicModel = data;
					TopicModelService.topicModelId = id;
					ITERS = data.IterCount
					console.log('iters', ITERS)
					$rootScope.$broadcast('topic-model-loaded');
				}).
				error(function (data, status, headers, config) {
					console.log("[FAILED]", "URL", url, "Results:", status, "Data:", data);
				});
		};

		TopicModelService.continueITM = function (data) {
			$rootScope.$broadcast("topic-model-loading");
			var data = {
					"action":"train",
					"termLimit": NUM_TERMS,
					"iters": ITERS+1,
					"mustLinks": data.must,
					"cannotLinks": data.cannot,
					"keepTerms": data.keep,
					"removeTerms": data.remove
				};
			var url = SERVER_URL;
			console.log("[LOADING]", "URL", url, "DATA", data);
			$http({
				url : url,
				data : $.param(data),
				method : 'POST',
				headers: {'Content-Type': 'application/x-www-form-urlencoded'}
			})
				.success(function (data, status, headers, config) {
					console.log("[LOADED]", "URL", url, "Results:", status, "Data:", data);
					TopicModelService.topicModel = data;
					ITERS = data.IterCount
					console.log('iters', ITERS)
					$rootScope.$broadcast('topic-model-loaded');
				}).error(function (data, status, headers, config) {
					console.log("[FAILED]", "URL", url, "Results:", status, "Data:", data);
				});
		};

		return TopicModelService;

	});
;
