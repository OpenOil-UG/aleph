aleph.controller('UserCtrl', ['$scope', '$uibModalInstance', 'OOUser',
	function($scope, $uibModalInstance, OOUser){
		  $scope.cancel = function(){
		      console.log('cancel');
		      $uibModalInstance.dismiss('cancel');
		  };

		  $scope.handle_login = function(){
		      $uibModalInstance.close($scope);
		  };

	          // XXX can we get rid of this duplication??
	          $scope.handle_register = $scope.handle_login; 

		  $scope.switch_to_register = function(){
		      $uibModalInstance.dismiss('cancel');
		      OOUser.registerModal($scope);
		      };

		  $scope.switch_to_login = function(){
		      $uibModalInstance.dismiss('cancel');
		      OOUser.loginModal($scope);
		      };


	      }]);

    
