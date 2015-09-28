from flask import Blueprint, request, redirect
from apikit import jsonify, Pager

from aleph import authz
from aleph.core import url_for, app
from aleph.model import Entity
from aleph.views.cache import etag_cache_keygen
from aleph.search.queries import document_query, get_list_facets
from aleph.search.attributes import available_attributes
from aleph.search import search_documents

from six.moves import urllib
import google_measurement_protocol

import logging
import uuid

blueprint = Blueprint('search', __name__)


def add_urls(doc):
    doc['archive_url'] = url_for('data.package',
                                 collection=doc.get('collection'),
                                 package_id=doc.get('id'))
    doc['manifest_url'] = url_for('data.manifest',
                                  collection=doc.get('collection'),
                                  package_id=doc.get('id'))
    return doc


def transform_facets(aggregations):
    coll = aggregations.get('all', {}).get('ftr', {}).get('collections', {})
    coll = coll.get('buckets', [])

    lists = {}
    for list_id in get_list_facets(request.args):
        key = 'list_%s' % list_id
        ents = aggregations.get(key, {}).get('inner', {})
        ents = ents.get('entities', {}).get('buckets', [])
        objs = Entity.by_id_set([e.get('key') for e in ents])
        entities = []
        for entity in ents:
            entity['entity'] = objs.get(entity.get('key'))
            if entity['entity'] is not None:
                entities.append(entity)
        lists[list_id] = entities

    attributes = {}
    for attr in request.args.getlist('attributefacet'):
        key = 'attr_%s' % attr
        vals = aggregations.get(key, {}).get('inner', {})
        vals = vals.get('values', {}).get('buckets', [])
        attributes[attr] = vals

    return {
        'sources': coll,
        'lists': lists,
        'attributes': attributes
    }

def preprocess_data(data):
    ordered_attribs = [
	  ['Company Name', ['Company Name', 'company_name', 'companyName', 'sedar_company_id', 'Company name', 'companyCode']],
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
                    break
        result['redirect_url'] = "https://search.openoil.net/api/1/exit?u=%s" % urllib.parse.quote(result.get('url', result.get('source_url', '')))
    return data

@blueprint.route('/api/1/query')
def query():
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
    data = preprocess_data(data)
    return jsonify(data)


@blueprint.route('/api/1/query/attributes')
def attributes():
    etag_cache_keygen()
    attributes = available_attributes(request.args,
        sources=authz.authz_sources('read'), # noqa
        lists=authz.authz_lists('read')) # noqa
    return jsonify(attributes)

@blueprint.route('/api/1/exit')
def exit_redirect():
    rawurl = request.args.get('u', 'https://search.openoil.net')
    newurl = urllib.parse.unquote(rawurl)
    # XXX tracking happens here, right?
    user_id = request.cookies.get('oo_search_user', 'unknown user')
    ua = app.config.get('GOOGLE_ANALYTICS_UA')
    view = google_measurement_protocol.PageView(
        path=request.url, referrer = request.referrer)
    google_measurement_protocol.report(
        ua, user_id, view)
    return redirect(newurl)
