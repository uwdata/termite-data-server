termite.controller("DataManager", function($scope, TopicModelService) {
  $scope.topicModels = [
      "nsf1k_mallet",
      "nsf10k_mallet",
      "nsf25k_mallet",
      "nsf146k_mallet",
      "20newsgroups_mallet"
    ];
  $scope.topicModel = $scope.topicModels[0];

  $scope.termLimits = [ 5, 7, 10, 15, 20 ] ;
  $scope.termLimit = $scope.termLmits[2];

  $scope.$on("topic-model-loaded") = function () {
    $("#loader").hide();
  }

  $scope.refresh = function () {
    // show the loader
    $("#loader").show();

    // get the requested topic model
    TopicModelService.getTopicModel($scope.topicModel, $scope.termLimit);
  };

});