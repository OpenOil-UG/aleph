from flask import Blueprint, request
from apikit import obj_or_404, request_data, jsonify

from aleph import authz
from aleph.core import db
from aleph.model import Alert
from aleph.views.cache import enable_cache

blueprint = Blueprint('alerts_api', __name__)


@blueprint.route('/api/1/alerts', methods=['GET'])
def index():
    if authz.logged_in():
        alerts = Alert.by_role(request.auth_role).all()
        return jsonify({'results': alerts, 'total': len(alerts)})
    return jsonify({'results': [], 'total': 0})


@blueprint.route('/api/1/alerts', methods=['POST', 'PUT'])
def create():
    # also handles update
    data = request.get_json()
    print(data)
    if 'query_text' not in data:
        return jsonify({'status': 'invalid'})
    authz.require(authz.logged_in())

    if data.get('alert_id', None): # UPDATE
        alert_id = int(data['alert_id'])
        alert = obj_or_404(Alert.by_id(alert_id))
        authz.require(alert.role_id == request.auth_role.id)
        alert.query_text = data['query_text']
        alert.custom_label = data.get('custom_label' '') or data['query_text']
        alert.checking_interval=int(data.get('checking_interval', 9))
    else: # CREATE
        alert = Alert(
            role_id = request.auth_role.id,
            query_text=data['query_text'],
            custom_label=data.get('custom_label', data['query_text']),
            checking_interval=int(data.get('checking_interval', 9))
         )
    db.session.add(alert)
    db.session.commit()
    return view(alert.id)


@blueprint.route('/api/1/alerts/<int:id>', methods=['GET'])
def view(id):
    enable_cache(vary_user=True)
    authz.require(authz.logged_in())
    alert = obj_or_404(Alert.by_id(id, role=request.auth_role))
    return jsonify(alert)


@blueprint.route('/api/1/alerts/<int:id>', methods=['DELETE'])
def delete(id):
    authz.require(authz.logged_in())
    alert = obj_or_404(Alert.by_id(id, role=request.auth_role))
    alert.delete()
    db.session.commit()
    return jsonify({'status': 'ok'})
