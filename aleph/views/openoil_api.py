from flask import Blueprint, abort, request
from apikit import obj_or_404, request_data, jsonify

from aleph import authz
from aleph.core import db
from aleph.model import Alert, Source
from aleph.views.cache import enable_cache
from aleph.views import search_api
from aleph.search.util import execute_basic

import requests
from six.moves import urllib

blueprint = Blueprint('openoil_api', __name__)

SRCS = {}

def get_source(sid):
    if sid not in SRCS:
        src = Source.by_id(sid)
        SRCS[sid] = src and src.label or ''
    return SRCS[sid]
    
@blueprint.route('/api/1/new_doc_count', methods=['GET'])
def new_doc_count():
    #XXX this needs to be cached
    query = {'query': {'range': {'created_at': {'gte': 'now-7d/d'}}}}
    res = execute_basic('document', query)
    total = res[1].get('total')
    return jsonify({'week': total})

result_element_whitelist = (
    "archive_url","attributes", "collection", "id", "manifest_url",
    "name","redirect_url","score","source_url", "title","updated_at", "filed_at",
)
# NB highlight is also used, but processed in result_filter

def flatten_attributes(data):
    for result in data['results']:
        new_attribs = {}
        old_attribs = result.pop('attributes')
        for att in old_attribs:
            new_attribs[att['name']] = att['value']
            result['attributes'] = new_attribs
    return data

def make_redirect_url(destination):
    # XXX this should use the correct hostame
    return "https://aleph.openoil.net/api/1/exit?u=%s" % urllib.parse.quote(destination.encode('utf8'))


def result_filter(rs):
    newlist = []
    attribute_items = {
        #newaleph     :  oldaleph
        'company_name': 'company_name',
        'filing_date': 'date',
        'file_size': 'filesize',
        'extension': 'format',
        'industry': 'industry'
        }
    base_items = {
        'source_url': 'source_url',
        'score': 'score',
        'title': 'title',
        'id': 'id',
        'created_at': 'updated_at',
        'file_name': 'name',
        'data_url': 'archive_url', # name retaied for backwards compatibility
        }
    for result in rs:
        newr = {
            'extract': [],
            'attributes': {},
        #    'unwanted': {}
        }
        newr['extract'] = [x['text'][0] for x in result['records']['results']]
        for k,v in result.items():
            if k in attribute_items:
                newr['attributes'][attribute_items[k]] = v
            elif k in base_items:
                newr[base_items[k]] = v
            #else:
            #    newr['unwanted'][k] = v
        newr['id'] = str(newr['id']) # keep backwards consistency
        if newr['source_url']:
            newr['redirect_url'] = make_redirect_url(newr['source_url'])
        # sources
        newr['source'] = get_source(result.get('source_id', None))
        newr['viewer_url'] = 'https://aleph.openoil.net/text/%s' % newr['id']
        newlist.append(newr)
    return newlist

def public_process_v1(data):
    '''
    put data in line with V1 api (ie old aleph)
    '''
    #data = flatten_attributes(data)
    data.pop('facets')
    data.pop('sources')
    # XXX this is incorrect -- it flips people from the public to the intern
    data['next_url'] = data.pop('next')
    data.pop('entities')
    data['results'] = result_filter(data['results'])
    nd = {}
    return data

def valid_api_key(request):
    key = request.args.get('apikey', 'INVALID')
    print(request.args)
    print('checking api key %s' % key)

    result = requests.get('http://api.openoil.net/apikey/check', params={'apikey': key})
    return result.status_code == 200
    

def preprocess_data(data):
    ordered_attribs = [
	  ['Company Name', ['Company Name', 'company_name', 'companyName', 'sedar_company_id', 'Company name', 'companyCode', 'company']],
	  ['Industry Sector', ['Industry Sector', 'industry', 'assignedSIC', 'sector_name']],
	  ['Filing Type', ['Filing Type', 'filing_type', 'file_type', 'document_type']],
	  ['Filing Date', ['Filing Date', 'date', 'filingDate', 'announcement_date']],	   
	   ]
    for result in data['results']:
        result['attribs_to_show'] = []
        for human_name, db_names in ordered_attribs:
            for attribute in result['attributes']:
                if attribute['name'] in db_names:
                    result['attribs_to_show'].append([human_name, attribute['value']])
                    result['top_attribs'], result['bottom_attribs'] = result['attribs_to_show'][:2], result['attribs_to_show'][2:]
                    break
        original_url = find_original_url(result) or ''
        result['redirect_url'] = make_redirect_url(original_url)
    return data


@blueprint.route('/aleph_api/1/query')
def query():
    if not valid_api_key(request):
        abort(403)
    from aleph.views.search_api import _query
    data = _query()
    #data = preprocess_data(data)
    data = public_process_v1(data)
    return jsonify(data)


