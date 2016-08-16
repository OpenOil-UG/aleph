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


blueprint = Blueprint('search_api', __name__)


@blueprint.route('/api/1/query')
def query():
    creds = authz.collections(authz.READ), authz.sources(authz.READ)
    enable_cache(vary_user=True, vary=creds)
    query = documents_query(request.args)
    query['size'] = get_limit(default=100)
    query['from'] = get_offset()
    result = execute_documents_query(request.args, query)
    params = next_params(request.args, result)
    if params is not None:
        result['next'] = url_for('search_api.query', **params)
    return jsonify(result)

def _query():
    '''
    everything here should be applicable both to the internal and to the
    public api
    '''
    creds = authz.collections(authz.READ), authz.sources(authz.READ)
    enable_cache(vary_user=True, vary=creds)
    query = documents_query(request.args)
    query['size'] = get_limit(default=100)
    query['from'] = get_offset()
    result = execute_documents_query(request.args, query)
    params = next_params(request.args, result)
    if params is not None:
        result['next'] = url_for('search_api.query', **params)
    return result
    '''
    etag_cache_keygen()
    query = document_query(request.args, lists=authz.authz_lists('read'),
                           sources=authz.authz_sources('read'),
                           highlights=True)
    results = search_documents(query)
    pager = Pager(results,
                  results_converter=lambda ds: [add_urls(d) for d in ds])
    data = pager.to_dict()
    #import ipdb; ipdb.set_trace()
    data['facets'] = transform_facets(results.result.get('aggregations', {}))
    return data
    '''



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
