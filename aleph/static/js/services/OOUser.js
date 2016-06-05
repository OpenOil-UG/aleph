aleph.factory('OOUser', ['$uibModal', '$http', '$q', 'Metadata', function($uibModal, $http, $q, Metadata) {

    var loginModal = function($scope, redirect_url, onsuccess){
	var onsuccess = onsuccess || function(data){
	    //Metadata.get();
	    $scope.$emit('loginStateChange', {});
	    Metadata.get().then(function(metadata) {
		console.log(metadata)
		//scope.roleName = metadata.session.role.name;
	    });

		}

	var mod = $uibModal.open({
                         templateUrl: 'templates/user/login_modal.html',
                         controller: 'UserCtrl',
                         backdrop: true
                     });
	  mod.result.then(
	      function(formdata){
		  console.log(formdata);
		  var email = formdata.formvalues.email;
		  var pw = formdata.formvalues.password;
		  //var email = $(mdl).find('[name=email]').val();
		  //var pw =  $(mdl).find('[name=password]').val();
		$http({
		    url: '/api/1/sessions/callback/ooemail',
		    method: 'GET', // XXX
		    params: {
			'email': email,
			'password': pw}
		}).success(onsuccess).error(function(data){
		    console.log('bad login'); //XXX needs user-facing error
		    });
},
	      function(){});
    }

    var registerModal = function($scope, redirect_url){
	var register_modal = $uibModal.open({
                         templateUrl: 'templates/user/register_modal.html',
                         controller: 'UserCtrl',
                         backdrop: true
                     });
	  register_modal.result.then(
	      function(mdl){
		  var email = mdl.formvalues.email;
		  var pw1 = mdl.formvalues.password1;
		  var pw2 = mdl.formvalues.password2;
		  if(pw1 != pw2){
		      // XXX need user-facing error here
		      console.log('passwords do not match');
		      return;
		  }
		  createAccount({email: email, pw: pw1}).success(function(data){
		      destination = ''; //XXX fixme legacy from old oo
		      if(destination == 'create_alert'){
			  $scope.makeAlertModal($scope, "Thank you for registering for Aleph");
		      }
		      else{
			  var d = $uibModal.open({
			      templateUrl: 'templates/user/register_completed.html',
			      controller: 'UserCtrl',
			      backdrop: true
			  });
			  // XXX we need to reload the navbar here
			  d.result.then(function(){window.location.reload();})
		      }
		      
		}).error(function(data){
		    // XXX add proper error-handling
		    console.log('bad registration details');
		    });


},
	      function(){});
    }

    
    var createAccount = function(params){
	return $http({
		    url: '/api/1/sessions/register/ooemail',
		    method: 'GET', // XXX
		  params: params,
	})
    }
    
    return {
	loginModal: loginModal,
	registerModal: registerModal,
	createAccount: createAccount,
    };

}]);
