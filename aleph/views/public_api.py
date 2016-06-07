from flask import Blueprint, abort, request
from apikit import jsonify
import requests

from aleph.views import search_api


blueprint = Blueprint('public', __name__)


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

def result_filter(rs):
    newlist = []
    for result in rs:
        newr = {
        'extract': []}
        for k,v in result.items():
            if k in result_element_whitelist:
                newr[k] = v
            if k == 'highlight' and 'summary' in v:
                newr['extract'] = v['summary']
        newlist.append(newr)
    return newlist

def public_process(data):
    data = flatten_attributes(data)
    data.pop('facets')
    data['results'] = result_filter(data['results'])
    nd = {}
    return data

def valid_api_key(request):
    key = request.args.get('apikey', 'INVALID')
    result = requests.get('http://api.openoil.net/apikey/check', params={'apikey': key})
    return result.status_code == 200
    

@blueprint.route('/aleph_api/1/query')
def query():
    if not valid_api_key(request):
        abort(403)
    data = search_api._query()
    data = search_api.preprocess_data(data)
    data = public_process(data)
    return jsonify(data)


