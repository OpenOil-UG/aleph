from flask import Blueprint, request
from flask.ext.login import current_user
from apikit import obj_or_404, request_data, jsonify

from aleph import authz
from aleph.model import Alert
from aleph.core import db
from aleph.validation import validate
#from aleph.views.cache import enable_cache

alerts_schema = 'https://aleph.grano.cc/operational/alert.json#'
blueprint = Blueprint('alerts', __name__)


@blueprint.route('/api/1/alerts', methods=['GET'])
def index():
    authz.require(authz.logged_in())
    #alerts = Alert.all(role=request.auth_role).all()
    alerts = db.session.query(Alert).filter(Alert.user_id == current_user.id).all()
    return jsonify({'results': alerts, 'total': len(alerts)})

@blueprint.route('/api/1/alerts', methods=['POST', 'PUT'])
def create():
    ''' should also handle update'''
    authz.require(authz.logged_in())
    data = request.get_json()
    print(data)
    validate(data, alerts_schema)
    if data['alert_id']: # UPDATE
        alert_id = int(data['alert_id'])
        alert = obj_or_404(Alert.by_id(alert_id))
        authz.require(alert.user_id == current_user.id)
        alert.query = data['query']
        alert.label = data.get('custom_label', data['query'])
        alert.checking_interval=int(data.get('checking_interval', 9))
    else: # CREATE
        alert = Alert(
            user_id = current_user.id,
            query=data['query'],
            label=data.get('custom_label', data['query']),
            checking_interval=int(data.get('checking_interval', 9))
        )
    db.session.add(alert)
    db.session.commit()
    return view(alert.id)

@blueprint.route('/api/1/alerts/<int:id>', methods=['GET'])
def view(id):
    authz.require(authz.logged_in())
    alert = obj_or_404(Alert.by_id(id))
    authz.require(alert.user_id == current_user.id)
    return jsonify(alert)

@blueprint.route('/api/1/alerts/delete/<int:id>')
@blueprint.route('/api/1/alerts/<int:id>', methods=['DELETE'])
def delete(id):
    authz.require(authz.logged_in())
    alert = obj_or_404(Alert.by_id(id))
    authz.require(alert.user_id == current_user.id)
    db.session.delete(alert)
    db.session.commit()
    return jsonify({'status': 'ok'})
