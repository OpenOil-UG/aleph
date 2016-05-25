
aleph.controller('AppCtrl', ['$scope', '$rootScope', '$routeParams', '$window', '$location', '$route', '$http', '$modal', '$q',
                             'Flash', 'Session', 'Query', 'Alert', 'QueryContext', '$sce',
			     function($scope, $rootScope, $routeParams, $window, $location, $route, $http, $modal, $q, Flash, Session, Query, Alert, QueryContext) {
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
    var d = $modal.open({
        templateUrl: 'alertscrud.html',
        controller: 'AlertsManageCtrl',
        backdrop: true,
	resolve: {
	    alerts: Alert.index()
	}
    });
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
		$http({
		    url: '/api/1/sessions/register/ooemail',
		    method: 'GET', // XXX
		    params: {
			'email': email,
			'pw': pw1}
		}).success(function(data){
		    Flash.message('Registered', 'success');		    
		    window.scp.session.logged_in = true;
		    $window.location.reload();
		}).error(function(data){
		    Flash.message('bad registration details', 'error');
		    });

},
	      function(){});
	  };
	      


     

      $scope.show_login_modal = function(){
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
		}).success(function(data){
		    Flash.message('logged in', 'success');		    
		    window.scp.session.logged_in = true;
		}).error(function(data){
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
		    postdata = {
			alert_id: formdata['alert_id'],
			query: formdata['alert_query'],
			custom_label: formdata['alert_label'],
			checking_interval: formdata['alert_frequency'],
		    }
		    $http({
			url: '/api/1/alerts',
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			data: JSON.stringify(postdata)
		    }).success(function(data){
			Flash.message('added email alert', 'success');
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

      if($location.search().intaction == 'login' && !session.logged_in){
	  $scope.show_login_modal();
      }
      if($location.search().intaction == 'register' && !session.logged_in){
	  $scope.show_register_modal();
      }

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
		    postdata = {
			alert_id: formdata['alert_id'],
			query: formdata['alert_query'],
			custom_label: formdata['alert_label'],
			checking_interval: formdata['alert_frequency'],
		    }
		    $http({
			url: '/api/1/alerts',
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			data: JSON.stringify(postdata)
		    }).success(function(data){
			Flash.message('added email alert', 'success');
			Alert.index().then(function(data){
			    $scope.alerts = data.results}
			 );

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
		    postdata = {
			alert_id: formdata['alert_id'],
			query: formdata['alert_query'],
			custom_label: formdata['alert_label'],
			checking_interval: formdata['alert_frequency'],
		    }
		    $http({
			url: '/api/1/alerts',
			method: 'POST',
			headers: {'Content-Type': 'application/json'},
			data: JSON.stringify(postdata)
		    }).success(function(data){
			Flash.message('added email alert', 'success');
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

