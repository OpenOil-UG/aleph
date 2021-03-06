aleph.controller('AppCtrl', ['$scope', '$rootScope', '$location', '$anchorScroll', '$route', '$http', '$uibModal', '$q', 'Alert', 'Metadata', 'OOUser', '$routeParams', '$window',
			     function($scope, $rootScope, $location, $anchorScroll, $route, $http, $uibModal, $q, Alert, Metadata, OOUser, $routeParams, $window) {

  $scope.session = {logged_in: false};
  $scope.routeLoaded = false;
  $scope.routeFailed = false;
  $scope.$route = $route;


  $scope.cancel = function() {
    $uibModalInstance.dismiss('cancel');
  };

  Metadata.get().then(function(metadata) {
    $scope.session = metadata.session;
  });

  $scope.$on('loginStateChange', function(event, args){
      Metadata.flush().then(function(metadata) {
	  $scope.session = metadata.session;
      });
      });


  $rootScope.$on('$routeChangeSuccess', function() {
        var output=$location.path()+"?";
        angular.forEach($routeParams,function(value,key){
            output+=key+"="+value+"&";
        })
      output=output.substr(0,output.length-1);
      $window.ga('send', 'pageview', output);
    });

  $rootScope.$on("$routeChangeStart", function (event, next, current) {
    $scope.reportLoading(true);
  });

  $rootScope.$on("$routeChangeSuccess", function (event, next, current) {
    $scope.reportLoading(false);
  });

  $rootScope.$on("$routeChangeError", function (event, next, current) {
    $scope.routeFailed = true;
  });

  $scope.keyDownNotify = function($event) {
    if(angular.lowercase($event.target.tagName) == 'body') {
      $scope.$broadcast('key-pressed', $event.keyCode);
    }
  };

  $rootScope.reportError = function(message) {
    $scope.routeFailed = true;
  };

  $rootScope.reportLoading = function(flag) {
    $scope.routeLoaded = !flag;
    if (flag) {
      $anchorScroll();
      $scope.routeFailed = false;
    }
  };

  $scope.editProfile = function($event) {
    $event.stopPropagation();
    var d = $uibModal.open({
        templateUrl: 'templates/profile.html',
        controller: 'ProfileCtrl',
        backdrop: true,
        resolve: {
          metadata: loadMetadata
        }
    });
  };

  $scope.manageAlerts = function($event) {
    $event.stopPropagation();
    var instance = $uibModal.open({
      templateUrl: 'templates/alerts_manage.html',
      controller: 'AlertsManageCtrl',
      backdrop: true,
      size: 'md',
      resolve: {
        alerts: Alert.index()
      }
    });
  };

 $scope.loginModal = function($event){   
     $event.stopPropagation();
     OOUser.loginModal($scope, '/');
 };

 $scope.registerModal = function($event){   
     $event.stopPropagation();
     OOUser.registerModal($scope, '/');
 };

				
}]);
