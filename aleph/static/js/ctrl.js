
aleph.controller('AppCtrl', ['$scope', '$rootScope', '$routeParams', '$window', '$location', '$route', '$http', '$modal', '$q',
                             'Flash', 'Session', 'Query', 'Alert', 'QueryContext', 'AlephUser', 
			     function($scope, $rootScope, $routeParams, $window, $location, $route, $http, $modal, $q, Flash, Session, Query, Alert, QueryContext, AlephUser) {
  $scope.session = {logged_in: false};
  $scope.query = Query;
  $scope.flash = Flash;
  $scope.sortorder = $scope.query.sort || ["best"];

  /*$scope.$watch('sortorder', function(){
      $scope.query.state.sort = $scope.sortorder;
      $scope.submitSearch();
      });*/

  window.scp = $scope;

				 
  // super-hacky temp redirect, to be removed soon
  if(['', '/'].indexOf($location.path()) > -1){
      $window.location.href="http://aleph.openoil.net";
  }

			


  source_labels = {
	'sec-edgar': 'US stock exchange filings',
	'edgar-partial-content': 'US stock exchange filings',
	'rigzone': 'Industry news',
	'lse': 'London stock exchange',
	'johannesburg-exchange': 'Johannesburg stock exchange',
	'asx': 'Australian stock exchange',
	'sedar-partial-content': 'Canadian corporate filings',
	'singapore-exchange': 'Singapore stock exchange',
	'openoil-contracts': 'OpenOil contract collection',
    }



  $scope.sourceLabel = function(key){
      if(key in source_labels){
	    return source_labels[key]}
	return key;
    }
				 

				 
				 
  Session.get(function(session) {
    $scope.session = session;
  });

  $rootScope.$on("$routeChangeStart", function (event, next, current) {
    Session.get(function(session) {
      if (next.$$route && next.$$route.loginRequired && !session.logged_in) {
        $location.search({});
        $location.path('/');
      }
    });
    $scope.query.state = Query.load();
  });

  $rootScope.$on('$routeChangeSuccess', function() {
        var output=$location.path()+"?";
        angular.forEach($routeParams,function(value,key){
            output+=key+"="+value+"&";
        })
      output=output.substr(0,output.length-1);
      $window.ga('send', 'pageview', output);
    });

  $scope.suggestEntities = function(prefix) {
    var dfd = $q.defer();
    var opts = {params: {'prefix': prefix}, ignoreLoadingBar: true};
    $http.get('/api/1/entities/_suggest', opts).then(function(res) {
      dfd.resolve(res.data.results);
    });
    return dfd.promise;
  }

  $scope.acceptSuggestion = function($item) {
    $scope.query.state.q = '';
    Query.toggleFilter('entity', $item.id);
  }

  $scope.editProfile = function() {
    var d = $modal.open({
        templateUrl: 'profile.html',
        controller: 'ProfileCtrl',
        backdrop: true
    });
  };

  $scope.alertsCRUD = function() {
      if(!$scope.session.logged_in){
	  $scope.show_login_modal('', function(data){
	      Flash.message('logged in', 'success');		    
	      window.scp.session.logged_in = true;
	      $scope.alertsCRUD();
	  });
      }
      else {
    var d = $modal.open({
        templateUrl: 'alertscrud.html',
        controller: 'AlertsManageCtrl',
        backdrop: true,
	resolve: {
	    alerts: Alert.index()
	}
    });
      }
  };

				 


  $scope.submitSearch = function(form) {
    $location.search($scope.query.state);
    if (Query.mode()) {
      $route.reload();
    } else {
      $location.path('/search');
    }
  };

      $scope.show_register_modal = function(message){
	  var register_modal = $modal.open({
	      templateUrl: 'user/register_modal.html',
	      backdrop: true,
	      controller: function($scope, $modalInstance, message){
		  $scope.cancel = function(){
		      $modalInstance.dismiss('cancel');
		  };

		  $scope.handle_register = function(){
		      $modalInstance.close($('#register_modal'));
		  };

		  $scope.switch_to_login = function(){
		      $modalInstance.dismiss('cancel');
		      window.scp.show_login_modal();
		      };

		  $scope.message = message;
	      },
	      resolve: {message: function(){return message;}},
	  });
	  register_modal.result.then(
	      function(mdl){
		  var email = $(mdl).find('[name=email]').val();
		  var pw1 =  $(mdl).find('[name=password1]').val();
		  var pw2 =  $(mdl).find('[name=password2]').val();
		  if(pw1 != pw2){
		      Flash.message('passwords do not match', 'error');
		      return;
		  }
		  AlephUser.createAccount({email: email, pw: pw1}).success(function(data){
		    Flash.message('Registered', 'success');		    
		    window.scp.session.logged_in = true;
		    $window.location.reload();
		}).error(function(data){
		    Flash.message('bad registration details', 'error');
		    });


},
	      function(){});
	  };
	      


     

 $scope.show_login_modal = function(message, onsuccess){
     onsuccess = onsuccess || function(data){
		    Flash.message('logged in', 'success');		    
		    window.scp.session.logged_in = true;
		}
     var login_modal = $modal.open({
	      templateUrl: 'user/login_modal.html',
	      backdrop: true,
	      controller: function($scope, $modalInstance){
		  $scope.cancel = function(){
		      $modalInstance.dismiss('cancel');
		  };

		  $scope.handle_login = function(){
		      $modalInstance.close($('#login_modal'));
		  };

		  $scope.switch_to_register = function(){
		      $modalInstance.dismiss('cancel');
		      window.scp.show_register_modal();
		      };

	      }

});
	  login_modal.result.then(
	      function(mdl){
		  var email = $(mdl).find('[name=email]').val();
		  var pw =  $(mdl).find('[name=password]').val();
		$http({
		    url: '/api/1/sessions/callback/ooemail',
		    method: 'GET', // XXX
		    params: {
			'email': email,
			'password': pw}
		}).success(onsuccess).error(function(data){
		    Flash.message('bad login', 'error');
		    });

},
	      function(){});
	  };
	      



    $scope.emailAlertButton = function(){
	Session.get(function(session) {
	    $scope.user = session.user;
	    $scope.session = session;
	});
	if(!$scope.session.logged_in){
	    $scope.show_register_modal('You need an account to create email alerts');
	    }
	else{
	    var emailModal = $modal.open({
		templateUrl: 'alert_create_form.html',
		controller: 'AlertCtrl',
		backdrop: true,
		resolve: {
		    formvalues: function () {
			return  {
			    searchTerm: $scope.query.state.q}
		    }
		}
	    });
	    emailModal.result.then(
		function (formdata) {
		    params = {
			alert_id: formdata['alert_id'],
			query: formdata['alert_query'],
			custom_label: formdata['alert_label'],
			checking_interval: formdata['alert_frequency'],
		    }
		    Alert.create(params).then(function(data){
			Flash.message('added email alert', 'success');
		    }, function(data){
			Flash.message('something went wrong', 'error');
		    })

		},
		function (result) {
		}
	    );
	}
    };



 								 
  $scope.clearSearch = function(form) {
    var mode = Query.mode();
    Query.clear();
    if (mode == 'table') {
      $route.reload();
    } else {
      $location.path('/search');
    }
  };

				 Session.get(function(session){ 
     if($location.search().intaction == 'profile'){
	 $scope.alertsCRUD();
      }
	 
      if($location.search().intaction == 'login' && !session.logged_in){
	  $scope.show_login_modal();
      }
      if($location.search().intaction == 'register' && !session.logged_in){
	  $scope.show_register_modal();
      }
				     $location.search('intaction', null);				     
				 });

}]);


aleph.controller('ProfileCtrl', ['$scope', '$location', '$modalInstance', '$http', 'Session',
  function($scope, $location, $modalInstance, $http, Session) {
  $scope.user = {};
  $scope.session = {};

  Session.get(function(session) {
    $scope.user = session.user;
    $scope.session = session;
  });

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

      $scope.update = function(form) {
	  console.log('scope update');
    var res = $http.post('/api/1/users/' + $scope.user.id, $scope.user);
    res.success(function(data) {
      $scope.user = data;
      $scope.session.user = data;
      $modalInstance.dismiss('ok');
    });
  };
  }]);

aleph.controller('AlertsManageCtrl', ['$scope', '$modalInstance', '$location', '$route', 'alerts', 'Alert', '$modal', '$http', 'Flash',
				      function($scope, $modalInstance, $location, $route, alerts, Alert, $modal, $http, Flash) {
	Alert.index().then(function(data){
	    $scope.alerts = data.results}
			 );

	$scope.editAlert = function(alert){
	    var emailModal = $modal.open({
		templateUrl: 'alert_create_form.html',
		controller: 'AlertCtrl',
		backdrop: true,
		resolve: {
		    formvalues: function(){
			return {
			    searchTerm: alert.query,
			    label: alert.label,
			    alert_id: alert.id,
			    frequency: alert.checking_interval
			}}
		}
	    });
	    emailModal.result.then(
		function (formdata) {
		    params = {
			alert_id: formdata['alert_id'],
			query: formdata['alert_query'],
			custom_label: formdata['alert_label'],
			checking_interval: formdata['alert_frequency'],
		    }
		    Alert.create(params).then(function(data){
			Flash.message('added email alert', 'success');
			Alert.index().then(function(data){
			    $scope.alerts = data.results}
			 );
		    }, function(data){
			Flash.message('something went wrong', 'error');
		    })

		},
		function (result) {
		}
	    );

	};

					  
	$scope.addAlert = function(){
	    var emailModal = $modal.open({
		templateUrl: 'alert_create_form.html',
		controller: 'AlertCtrl',
		backdrop: true,
		resolve: {
		    formvalues: function(){ return {}}
		}
	    });
	    emailModal.result.then(
		function (formdata) {
		    params = {
			alert_id: formdata['alert_id'],
			query: formdata['alert_query'],
			custom_label: formdata['alert_label'],
			checking_interval: formdata['alert_frequency'],
		    }
		    Alert.create(params).then(function(data){
			Flash.message('added email alert', 'success');
		    }, function(data){
			Flash.message('Something went wrong', 'error');
		    })
		},
		function (result) {
		}
	    );

	};

  $scope.removeAlert = function(alert) {
    Alert.delete(alert.id).then(function() {
      $scope.alerts.splice($scope.alerts.indexOf(alert), 1)
    });
  };

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

  $scope.close = function(form) {
    $modalInstance.close();
    $route.reload();
  };

}]);



aleph.controller('AlertProfileCtrl', ['$scope', '$location', '$modalInstance', '$http', 'Session',
  function($scope, $location, $modalInstance, $http, Session) {
  $scope.user = {};
  $scope.session = {};

  Session.get(function(session) {
    $scope.user = session.user;
    $scope.session = session;
  });

  $scope.cancel = function() {
    $modalInstance.dismiss('cancel');
  };

      $scope.addInterface = function(form){
	  console.log("creating new alert -- modal window");
      };
      
      
      $scope.addSubmit = function(form){
	  console.log("creating new alert");
      };

      $scope.remove = function(alertid){
	  console.log("deleting an alert");
      }

      $scope.updateSubmit = function(form){
	  console.log("updating an alert");
      }

    }]);  


aleph.controller('SignupCtrl', ['$scope', '$location', '$http', 'Session', 'AlephUser', 'Alert', 'Flash',
				function($scope, $location, $http, Session, AlephUser, Alert, Flash)
{
    submitRegistration = function(success, failure){
    }
    $scope.rf = {}
    $scope.submitSignup = function(data){
	params = {'email': $scope.rf.email,
		  'pw': $scope.rf.password1}
	AlephUser.createAccount(params).success(function(data){
	    $scope.rf.invalid = null;
	    //create the alert
	    Alert.create({
		alert_id: null,
		query: $scope.rf.searchTerm,
		checking_interval: $scope.rf.frequency,
	    }).then(function(data){
		$location.path("/signup_complete");
		Flash.message('added email alert', 'success');
	    }, function(data){
		$scope.rf.invalid = 'Could not create an alert';
				    })

	    console.log(data)}).error(function(data){
		$scope.rf.invalid = 'Could not create this acocunt';
		});
	// create an account and login
	// error --> display error messages

	// success --> create an alert
    }
}]);



aleph.controller('AlertCtrl', ['$scope', '$location', '$modalInstance', '$http', 'Session', 'formvalues',
			       function($scope, $location, $modalInstance, $http, Session, formvalues)
{
    defaults = {
	searchTerm: "",
	frequency: 7,
	alert_id: null,
	label: "",
    }
    $scope.formvalues = jQuery.extend({}, defaults, formvalues);

				   
    $scope.cancel = function(){
	$modalInstance.dismiss('cancel');
	};
    $scope.emailAlertSubmit = function(form){
	var formdata = {}
	$.each($('[name=alertForm]').serializeArray(), function(i, field) {
	    formdata[field.name] = field.value;
	});
	$modalInstance.close(formdata);
	};
}]); 

