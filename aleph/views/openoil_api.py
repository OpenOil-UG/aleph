from flask import Blueprint, request
from apikit import obj_or_404, request_data, jsonify

from aleph import authz
from aleph.core import db
from aleph.model import Alert
from aleph.views.cache import enable_cache
from aleph.search.util import execute_basic

blueprint = Blueprint('openoil_api', __name__)


@blueprint.route('/api/1/new_doc_count', methods=['GET'])
def new_doc_count():
    #XXX this needs to be cached
    query = {'query': {'range': {'created_at': {'gte': 'now-7d/d'}}}}
    res = execute_basic('document', query)
    total = res[1].get('total')
    return jsonify({'week': total})
