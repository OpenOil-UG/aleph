
aleph.factory('Session', ['$http', '$q', function($http, $q) {
    var dfd = null;

    var reset = function() {
        dfd = null;
    };

    var get = function(cb) {
        if (dfd === null) {
            var dt = new Date();
            var config = {cache: false, params: {'_': dt.getTime()}};
            dfd = $http.get('/api/1/sessions', config);
        }
        dfd.success(function(data) {
          data.cbq = data.logged_in ? data.user.id : 'anon';
          cb(data);
        });
    };

    return {
        get: get,
        reset: reset
    };
}]);


aleph.factory('Flash', ['$rootScope', '$timeout', function($rootScope, $timeout) {
  // Message flashing.
  var currentMessage = null;

  $rootScope.$on("$routeChangeSuccess", function() {
    currentMessage = null;
  });

  return {
    message: function(message, type) {
      currentMessage = [message, type];
      $timeout(function() {
        currentMessage = null;
      }, 2000);
    },
    getMessage: function() {
      return currentMessage;
    }
  };
}]);


aleph.factory('Validation', ['Flash', function(Flash) {
  // handle server-side form validation errors.
  return {
    handle: function(form) {
      return function(res) {
        if (res.status == 400 || !form) {
          var errors = [];
          
          for (var field in res.errors) {
            form[field].$setValidity('value', false);
            form[field].$message = res.errors[field];
            errors.push(field);
          }
          if (angular.isDefined(form._errors)) {
            angular.forEach(form._errors, function(field) {
              if (errors.indexOf(field) == -1 && form[field]) {
                form[field].$setValidity('value', true);
              }
            });
          }
          form._errors = errors;
        } else {
          Flash.message(res.message || res.title || 'Server error', 'danger');
        }
      }
    }
  };
}]);


aleph.factory('Alert', ['$http', '$q', '$location', '$sce', 'Session',
    function($http, $q, $location, $sce, Session) {

	return {
	    nindex: function(id){
		return $http.get('/api/1/alerts').then(function(response) {    
		    return response.data;
		});
	    },
      index: function(id) {

	  
	  var defer = $q.defer();
	  $http.get('/api/1/alerts').then(function(response){
	      defer.resolve(response.data);});
	  return defer.promise;
	  /*
      var dfd = $q.defer(),
          url = '/api/1/alerts';
	
      Session.get(function(session) {
        $http.get(url).then(function(res) {
	    console.log('got some data from the backend');
	    console.log(res.data);
          dfd.resolve(res.data);
        }, function(err) {
          dfd.reject(err);
        });
      });
      return dfd.promise;*/
    },
    delete: function(id) {
      return $http.delete('/api/1/alerts/' + id);
    },
    create: function(query) {
      var dfd = $q.defer();
      $http.post('/api/1/alerts', {'query': query}).then(function(res) {
        dfd.resolve(res.data);
      }, function(err) {
        dfd.reject(err);
      });
      return dfd.promise;
    }
  };
}]);
