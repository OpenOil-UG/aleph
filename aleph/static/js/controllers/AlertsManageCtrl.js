aleph.controller('AlertsManageCtrl', ['$scope', '$uibModalInstance', '$location', '$route', 'alerts', 'Alert', '$uibModal',
    function($scope, $uibModalInstance, $location, $route, alerts, Alert, $uibModal) {

  $scope.alerts = alerts.results;

  $scope.openQuery = function(alert) {
    $location.path('/search');
    $location.search({'q': alert.query_text, 'entity': alert.entity_id});
    $uibModalInstance.close();
  };

  $scope.editAlert = function(alert) {
    console.log('about to edit');
    $uibModalInstance.close();
    Alert.edit(alert).then(function(){
	$uibModal.open({
	    templateUrl: 'templates/alerts_manage.html',
	    controller: 'AlertsManageCtrl',
	    backdrop: true,
	    size: 'md',
	    resolve: {
		alerts: Alert.index()
	    }
	});
      });
      };

  $scope.removeAlert = function(alert) {
    Alert.delete(alert.id).then(function() {
      $scope.alerts.splice($scope.alerts.indexOf(alert), 1)
    });
  };

  $scope.cancel = function() {
    $uibModalInstance.dismiss('cancel');
  };

  $scope.close = function(form) {
    $uibModalInstance.close();
    $route.reload();
  };

}]);
