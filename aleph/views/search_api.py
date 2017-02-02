from flask import Blueprint, request
from apikit import jsonify
from apikit import get_limit, get_offset

from aleph import authz
from aleph.core import url_for
from aleph.model import Alert
from aleph.views.cache import enable_cache
from aleph.views.util import get_document
from aleph.search import documents_query, execute_documents_query
from aleph.search import records_query, execute_records_query
from aleph.search.util import next_params
from elasticsearch import TransportError

blueprint = Blueprint('search_api', __name__)


@blueprint.route('/api/1/query')
def query():
    # XXX this should be just _query wrapped in jsonify
    try:
        result = _query(escape=False)
    except TransportError:
        # Try it again, but filter special characters away from ES
        result = _query(escape=True)
    return jsonify(result)

def _query(escape=False):
    '''
    everything here should be applicable both to the internal and to the
    public api
    '''
    creds = authz.collections(authz.READ), authz.sources(authz.READ)
    enable_cache(vary_user=True, vary=creds)
    query = documents_query(request.args, escape=escape)
    query['size'] = get_limit(default=100)
    query['from'] = get_offset()
    result = execute_documents_query(request.args, query)
    params = next_params(request.args, result)
    if params is not None:
        result['next'] = url_for('search_api.query', **params)
    return result


@blueprint.route('/api/1/query/records/<int:document_id>')
def records(document_id):
    document = get_document(document_id)
    enable_cache(vary_user=True)
    query = records_query(document.id, request.args)
    if query is None:
        return jsonify({
            'status': 'ok',
            'message': 'no query'
        })
    query['size'] = get_limit(default=30)
    query['from'] = get_offset()
    result = execute_records_query(query)
    params = next_params(request.args, result)
    if params is not None:
        result['next'] = url_for('search_api.record', document_id=document_id,
                                 **params)
    return jsonify(result)
