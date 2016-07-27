
aleph.factory('Alert', ['$http', '$q', '$location', '$sce', '$uibModal', 'Metadata',
    function($http, $q, $location, $sce, $uibModal, Metadata) {
  var indexDfd = null, indexAlerts = null;

  function index() {
    if (indexDfd === null) {
      indexDfd = $q.defer();
      Metadata.get().then(function(metadata) {
        indexAlerts = [];
        if (!metadata.session.logged_in) {
          indexDfd.resolve({total: 0, results: []});
        } else {
          $http.get('/api/1/alerts', {ignoreLoadingBar: true}).then(function(res) {
            indexAlerts = res.data.results;
            indexDfd.resolve(res.data);
          }, function(err) {
            indexDfd.reject(err);
          });  
        }
      });
    }
    return indexDfd.promise;
  };

  function flush() {
    indexDfd = null;
    indexAlerts = null;
    return index();
  };

  function deleteAlert(id) {
    var dfd = $q.defer();
    $http.delete('/api/1/alerts/' + id).then(function(res) {
      flush().then(function() {
        dfd.resolve(id);
      }, function(err) {
        dfd.reject(err);
      });
    });
    return dfd.promise;
  };

  function editAlert(alert){
      console.log('editAlert');
      console.log(alert);
      var editAlertModal = $uibModal.open({
                templateUrl: 'templates/alert_create_form.html',
                //controller: 'AlertsManageCtrl',
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
            editAlertModal.result.then(
                function (formdata) {
                    params = {
                        alert_id: formdata['alert_id'],
                        query: formdata['alert_query'],
                        custom_label: formdata['alert_label'],
                        checking_interval: formdata['alert_frequency'],
                    }
		    console.log('oh boy');
                    /*Alert.create(params).then(function(data){
                        $scope.message = 'Edited your email alert';
                        Alert.index().then(function(data){
                            $scope.alerts = data.results}
                         );
                    }, function(data){
                        Flash.message('something went wrong', 'error');
                    })*/

                },
                function (result) {
                }
            );	    
	}

  function createAlert(alert) {
    var dfd = $q.defer();
    $http.post('/api/1/alerts', alert).then(function(res) {
      flush().then(function() {
        dfd.resolve(res.data.id);
      }, function(err) {
        dfd.reject(err);
      });
    }, function(err) {
      dfd.reject(err);
    });
    return dfd.promise;
  };

  function checkAlert(alert) {
    // this is a sync function, but it is premised on alerts already being loaded. 
    // use with care.
    if (indexAlerts == null) {
      return false;
    }
    // normalize
    if (alert.query_text && alert.query_text.trim().length < 2) {
      alert.query_text = null;
    }
    for (var i in indexAlerts) {
      var candidate = indexAlerts[i], 
          sameId = candidate.entity_id == alert.entity_id,
          sameQuery = alert.query_text && candidate.query_text && alert.query_text.toLowerCase() == candidate.query_text.toLowerCase();
      if (!candidate.entity_id && !alert.entity_id && sameQuery) {
        return candidate.id;
      } else if (!candidate.query_text && !alert.query_text && sameId) {
        return candidate.id;
      } else if (sameId && sameQuery) {
        return candidate.id;
      }
    }
    return false;
  };

  function toggleAlert(alert) {
    var alertId = checkAlert(alert);
    if (!alertId) {
      return createAlert(alert);
    }
    return deleteAlert(alertId);
  };

  function validAlert(alert) {
    if (alert.query_text && alert.query_text.trim().length >= 2) {
      return true;
    }
    if (alert.entity_id) {
      return true
    }
    return false;
  };

  return {
    index: index,
    check: checkAlert,
    toggle: toggleAlert,
    delete: deleteAlert,
    edit: editAlert,
    create: createAlert,
    valid: validAlert
  };
}]);
