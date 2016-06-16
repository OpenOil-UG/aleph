
aleph.controller('HomeCtrl', ['$scope', '$location', '$route', 'Source', 'Collection', 'Authz', 'Role', 'Title', 'data', 'metadata', '$http',
			      function($scope, $location, $route, Source, Collection, Authz, Role, Title, data, metadata, $http) {

  $scope.suggestions = [
    {
      label: 'Nigeria incorporated',
      href: 'https://search.openoil.net/#/search?q=Nigeria incorporated'
    },
    {
      label: 'Doubt going concern',
      href: 'https://search.openoil.net/#/search?q="doubt going concern"~10'
    },
    {
      label: 'Statement of reserves',
      href: 'https://search.openoil.net/#/search?q=reserve%20statement'
    }
  ];
	
  $scope.result = data.result;
  $scope.sources = data.sources;
  $scope.session = metadata.session;
  $scope.metadata = metadata;
  $scope.collections = metadata.collectionsList.sort(function(a, b) {
    return a.label.localeCompare(b.label);
  });
  $scope.title = Title.getSiteTitle();
  $scope.query = {q: ''};
  $scope.authz = Authz;


  $scope.submitSearch = function(form) {
    $location.path('/search');
    $location.search({q: $scope.query.q});
  };

  $scope.editSource = function(source, $event) {
    $event.stopPropagation();
    Source.edit(source).then(function() {
      $route.reload();
    });
  };

  $scope.editCollection = function(collection, $event) {
    $event.stopPropagation();
    Collection.edit(collection).then(function() {
      $route.reload();
    });
  };

	$scope.docs_this_week = 'many';
	$http.get('/api/1/new_doc_count').then(function(res){
	    $scope.docs_this_week = res.data['week']});
}]);
