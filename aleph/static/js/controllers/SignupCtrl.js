aleph.controller('SignupCtrl',
		 ['$scope', '$location', '$http', 'Session',
  function($scope, $location){
      $scope.master = {};
      $scope.sendfom = function(){
	  console.log('submitting');
	  };
  }]);				
