aleph.controller('UserCtrl', ['$scope', '$uibModalInstance',
	function($scope, $uibModalInstance){
   
		  $scope.cancel = function(){
		      $uibModalInstance.dismiss('cancel');
		  };

		  $scope.handle_login = function(){
		      $uibModalInstance.close($scope);
		  };

	          // XXX can we get rid of this duplication??
	          $scope.handle_register = $scope.handle_login; 

		  $scope.switch_to_register = function(){
		      $uibModalInstance.dismiss('cancel');
		      window.scp.show_register_modal();
		      };

	      }]);

    
