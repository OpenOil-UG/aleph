
aleph.controller('HomeCtrl', ['$scope', '$location', '$route', 'Source', 'Collection', 'Authz', 'Role', 'Title', 'data', 'metadata', '$http',
			      function($scope, $location, $route, Source, Collection, Authz, Role, Title, data, metadata, $http) {

  $scope.suggestions = [
    {
      label: 'Bob Dudley',
      href: 'http://aleph.openoil.net/#/search?q="Bob Dudley"'
    },
    {
      label: 'financial statement',
      href: 'http://aleph.openoil.net/#/search?q="financial statement"'
    },
    {
      label: 'climate change policy',
      href: 'http://aleph.openoil.net/#/search?q="our climate change policy"~20'
    }
  ];
	
	jQuery(document).ready(function() {
	    $('.video').fancybox({
		openEffect  : 'none',
		closeEffect : 'none',
		helpers : {
			media : {}
		}
	    });

	});

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
